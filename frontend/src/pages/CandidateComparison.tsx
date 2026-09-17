import { useEffect, useState } from 'react'
import {
  compareCandidates,
  getComparisonExplanation,
  getCandidates,
  getJobProfile,
  type CandidateResultResponse,
  type CandidateComparisonExplanationResponse,
  type JobProfileResponse,
} from '../services/api'

interface CandidateComparisonProps {
  jobId: number | null
  onBack: () => void
}

interface ComparisonCandidate {
  id: string
  name: string
  rank: number | null
  score: number | null
  requiredCoverage: string
  requiredPercentage: number
  preferredCoverage: string
  experience: string
  education: string
  responsibilitiesScore: number
  matchedSkills: string[]
  gaps: string[]
  evidence: string
}

function getCandidateName(
  candidate: CandidateResultResponse,
): string {
  const name = candidate.candidate.profile.name

  if (typeof name === 'string' && name.trim()) {
    return name
  }

  return candidate.candidate.source_filename
}

function getProfileExperience(
  candidate: CandidateResultResponse,
): string {
  const experience = candidate.candidate.profile
    .experience_years

  if (typeof experience !== 'number') {
    return 'Not provided'
  }

  return `${experience} ${experience === 1 ? 'year' : 'years'}`
}

function getProfileEducation(
  candidate: CandidateResultResponse,
): string {
  const education = candidate.candidate.profile.education

  if (!Array.isArray(education) || education.length === 0) {
    return 'Not provided'
  }

  return education.join(', ')
}

function getScoreBreakdownValue(
  candidate: CandidateResultResponse,
  key: string,
): number {
  const value = candidate.score_breakdown[key]

  return typeof value === 'number' ? value : 0
}

function getSkillMatches(
  candidate: CandidateResultResponse,
): Array<{
  name: string
  normalizedName: string
  status: string
}> {
  const matches = candidate.match_result.skill_matches

  if (!Array.isArray(matches)) {
    return []
  }

  return matches
    .filter(
      (match) =>
        match !== null &&
        typeof match === 'object',
    )
    .map((match) => {
      const item = match as Record<string, unknown>

      const skill =
        item.skill &&
        typeof item.skill === 'object'
          ? (item.skill as Record<string, unknown>)
          : null

      const name =
        skill && typeof skill.name === 'string'
          ? skill.name
          : 'Unknown skill'

      const normalizedName =
        skill &&
        typeof skill.normalized_name === 'string'
          ? skill.normalized_name
          : name.toLowerCase()

      const status =
        typeof item.status === 'string'
          ? item.status
          : 'missing'

      return {
        name,
        normalizedName,
        status,
      }
    })
}

function getEvidence(
  candidate: CandidateResultResponse,
): string {
  const evidence = candidate.match_result.evidence

  if (!Array.isArray(evidence)) {
    return 'No evidence found.'
  }

  const texts = evidence
    .filter(
      (item) =>
        item !== null &&
        typeof item === 'object',
    )
    .map((item) => {
      const evidenceItem =
        item as Record<string, unknown>

      return typeof evidenceItem.text === 'string'
        ? evidenceItem.text
        : ''
    })
    .filter(Boolean)

  if (texts.length === 0) {
    return 'No evidence found.'
  }

  return texts.join(' ')
}

function mapCandidate(
  candidate: CandidateResultResponse,
  jobProfile: JobProfileResponse,
): ComparisonCandidate {
  const skills = getSkillMatches(candidate)

  const preferredSkillNames = new Set(
    jobProfile.preferred_skills.map(
      (skill) => skill.normalized_name,
    ),
  )

  const preferredMatches = skills.filter(
    (skill) =>
      preferredSkillNames.has(skill.normalizedName) &&
      skill.status !== 'missing',
  )

  const matchedSkills = skills
    .filter(
      (skill) =>
        skill.status === 'matched' ||
        skill.status === 'partial',
    )
    .map((skill) => skill.name)

  const gaps = skills
    .filter((skill) => skill.status === 'missing')
    .map((skill) => skill.name)

  const preferredTotal =
    jobProfile.preferred_skills.length

  return {
    id: String(candidate.candidate.id),
    name: getCandidateName(candidate),
    rank: candidate.rank,
    score: candidate.overall_score,
    requiredCoverage:
      candidate.required_skill_coverage
        ? `${candidate.required_skill_coverage.matched} / ${candidate.required_skill_coverage.total}`
        : '0 / 0',
    requiredPercentage:
      candidate.required_skill_coverage?.percentage ?? 0,
    preferredCoverage:
      `${preferredMatches.length} / ${preferredTotal}`,
    experience: getProfileExperience(candidate),
    education: getProfileEducation(candidate),
    responsibilitiesScore:
      getScoreBreakdownValue(
        candidate,
        'responsibilitiesAlignment',
      ) ||
      getScoreBreakdownValue(
        candidate,
        'responsibilities_alignment',
      ),
    matchedSkills,
    gaps,
    evidence: getEvidence(candidate),
  }
}

function CandidateComparison({
  jobId,
  onBack,
}: CandidateComparisonProps) {
  const [candidates, setCandidates] = useState<
    ComparisonCandidate[]
  >([])

  const [selectedCandidateIds, setSelectedCandidateIds] =
    useState<string[]>([])

  const [jobProfile, setJobProfile] =
    useState<JobProfileResponse | null>(null)

  const [
    comparisonCandidates,
    setComparisonCandidates,
  ] = useState<ComparisonCandidate[]>([])

  const [comparisonExplanation, setComparisonExplanation] =
    useState<CandidateComparisonExplanationResponse | null>(
      null,
    )

  const [showComparison, setShowComparison] =
    useState(false)

  const [loading, setLoading] = useState(true)
  const [comparisonLoading, setComparisonLoading] =
    useState(false)

  const [error, setError] = useState<string | null>(null)
  const [
    comparisonError,
    setComparisonError,
  ] = useState<string | null>(null)

  useEffect(() => {
    if (jobId === null) {
      return
    }

    let cancelled = false

    const loadCandidates = async () => {
      setLoading(true)
      setError(null)

      try {
        const [
          profileResponse,
          candidatesResponse,
        ] = await Promise.all([
          getJobProfile(jobId),
          getCandidates(jobId),
        ])

        if (cancelled) {
          return
        }

        setJobProfile(profileResponse)

        setCandidates(
          candidatesResponse.candidates.map(
            (candidate) =>
              mapCandidate(
                candidate,
                profileResponse,
              ),
          ),
        )
      } catch (err) {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load candidates.',
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadCandidates()

    return () => {
      cancelled = true
    }
  }, [jobId])

  const toggleCandidate = (
    candidateId: string,
  ) => {
    setSelectedCandidateIds((current) => {
      if (current.includes(candidateId)) {
        return current.filter(
          (id) => id !== candidateId,
        )
      }

      if (current.length >= 3) {
        return current
      }

      return [...current, candidateId]
    })

    setShowComparison(false)
    setComparisonCandidates([])
    setComparisonExplanation(null)
    setComparisonError(null)
  }

  const handleCompare = async () => {
    if (
      jobId === null ||
      selectedCandidateIds.length < 2
    ) {
      return
    }

    setComparisonLoading(true)
    setComparisonError(null)
    setComparisonExplanation(null)

    try {
      const candidateIds =
        selectedCandidateIds.map(Number)

      const [
        comparisonResponse,
        explanationResponse,
      ] = await Promise.all([
        compareCandidates(
          jobId,
          candidateIds,
        ),
        getComparisonExplanation(
          jobId,
          candidateIds,
        ),
      ])

      if (!jobProfile) {
        throw new Error(
          'Job profile is unavailable.',
        )
      }

      setComparisonCandidates(
        comparisonResponse.candidates.map(
          (candidate) =>
            mapCandidate(
              candidate,
              jobProfile,
            ),
        ),
      )

      setComparisonExplanation(
        explanationResponse,
      )

      setShowComparison(true)

      window.setTimeout(() => {
        document
          .querySelector('.comparison-results')
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          })
      }, 0)
    } catch (err) {
      setComparisonError(
        err instanceof Error
          ? err.message
          : 'Failed to compare candidates.',
      )
    } finally {
      setComparisonLoading(false)
    }
  }

  return (
    <div className="comparison-page">
      <button
        type="button"
        className="comparison-back-button"
        onClick={onBack}
      >
        <span aria-hidden="true">←</span>
        Back to candidates
      </button>

      <section className="comparison-intro">
        <div>
          <span className="page-eyebrow">
            Candidate comparison
          </span>

          <h2>
            Put the strongest matches side by side.
          </h2>

          <p>
            Select up to three candidates to compare their matching signals,
            evidence and skill gaps before making a recruiter decision.
          </p>
        </div>

        <div className="comparison-selection-count">
          <strong>
            {selectedCandidateIds.length}
          </strong>

          <span>of 3 selected</span>
        </div>
      </section>

      <section className="comparison-selection">
        <div className="comparison-selection-header">
          <div>
            <span>Candidate shortlist</span>
            <h3>Select candidates to compare</h3>
          </div>

          <span>Choose 2–3 candidates</span>
        </div>

        {loading && (
          <div className="dashboard-empty">
            <strong>Loading candidates...</strong>
            <span>
              Retrieving the screening results.
            </span>
          </div>
        )}

        {!loading && error && (
          <div className="dashboard-empty">
            <strong>
              Unable to load candidates.
            </strong>
            <span>{error}</span>
          </div>
        )}

        {!loading &&
          !error &&
          candidates.length === 0 && (
            <div className="dashboard-empty">
              <strong>
                No candidates available.
              </strong>
              <span>
                Process candidates before starting a comparison.
              </span>
            </div>
          )}

        {!loading &&
          !error &&
          candidates.length > 0 && (
            <div className="comparison-candidate-list">
              {candidates.map((candidate) => {
                const selected =
                  selectedCandidateIds.includes(
                    candidate.id,
                  )

                return (
                  <button
                    key={candidate.id}
                    type="button"
                    className={`comparison-candidate-option ${
                      selected ? 'selected' : ''
                    }`}
                    onClick={() =>
                      toggleCandidate(
                        candidate.id,
                      )
                    }
                  >
                    <span className="comparison-checkbox">
                      {selected ? '✓' : ''}
                    </span>

                    <span className="comparison-option-avatar">
                      {candidate.name
                        .split(' ')
                        .map(
                          (name) => name[0],
                        )
                        .join('')}
                    </span>

                    <span className="comparison-option-info">
                      <strong>
                        {candidate.name}
                      </strong>

                      <small>
                        Rank #
                        {candidate.rank ?? '—'} ·{' '}
                        {candidate.requiredCoverage}{' '}
                        required
                      </small>
                    </span>

                    <span className="comparison-option-score">
                      {candidate.score !== null
                        ? `${candidate.score}%`
                        : '—'}
                    </span>
                  </button>
                )
              })}
            </div>
          )}

        <div className="comparison-selection-actions">
          <span>
            {selectedCandidateIds.length < 2
              ? 'Select at least two candidates'
              : `${selectedCandidateIds.length} candidates ready to compare`}
          </span>

          <button
            type="button"
            className="comparison-compare-button"
            disabled={
              selectedCandidateIds.length < 2 ||
              comparisonLoading
            }
            onClick={handleCompare}
          >
            {comparisonLoading
              ? 'Comparing...'
              : 'Compare selected'}

            <span aria-hidden="true">→</span>
          </button>
        </div>
      </section>

      {comparisonError && (
        <div className="dashboard-empty">
          <strong>
            Unable to compare candidates.
          </strong>

          <span>{comparisonError}</span>
        </div>
      )}

      {showComparison &&
        comparisonCandidates.length >= 2 && (
          <>
            <section className="comparison-results">
              <div className="comparison-results-header">
                <div>
                  <span>Evidence comparison</span>
                  <h3>Candidate differences</h3>
                </div>

                <span>
                  Matching engine results
                </span>
              </div>

              <div className="comparison-table-wrapper">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>Dimension</th>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <th key={candidate.id}>
                            <div className="comparison-table-candidate">
                              <strong>
                                {candidate.name}
                              </strong>

                              <span>
                                Rank #
                                {candidate.rank ??
                                  '—'}
                              </span>
                            </div>
                          </th>
                        ),
                      )}
                    </tr>
                  </thead>

                  <tbody>
                    <tr>
                      <td>Overall fit</td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <strong className="comparison-score">
                              {candidate.score !==
                              null
                                ? `${candidate.score}%`
                                : '—'}
                            </strong>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>
                        Required skill coverage
                      </td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <strong>
                              {
                                candidate.requiredCoverage
                              }
                            </strong>

                            <span className="comparison-metric-detail">
                              {
                                candidate.requiredPercentage
                              }
                              % coverage
                            </span>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>
                        Preferred skill coverage
                      </td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <strong>
                              {
                                candidate.preferredCoverage
                              }
                            </strong>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>
                        Relevant experience
                      </td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            {candidate.experience}
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>Education</td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            {candidate.education}
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>
                        Responsibilities alignment
                      </td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <strong>
                              {
                                candidate.responsibilitiesScore
                              }
                              %
                            </strong>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>Matched skills</td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <div className="comparison-skill-list">
                              {candidate.matchedSkills.map(
                                (skill) => (
                                  <span
                                    key={skill}
                                    className="comparison-skill matched"
                                  >
                                    {skill}
                                  </span>
                                ),
                              )}
                            </div>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>Skill gaps</td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <div className="comparison-skill-list">
                              {candidate.gaps.map(
                                (gap) => (
                                  <span
                                    key={gap}
                                    className="comparison-skill gap"
                                  >
                                    {gap}
                                  </span>
                                ),
                              )}
                            </div>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <td>
                        Supporting evidence
                      </td>

                      {comparisonCandidates.map(
                        (candidate) => (
                          <td key={candidate.id}>
                            <p className="comparison-evidence">
                              {candidate.evidence}
                            </p>
                          </td>
                        ),
                      )}
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section className="comparison-ai-panel">
              <div className="comparison-results-header">
                <div>
                  <span>
                    Grounded explanation
                  </span>

                  <h3>
                    What the evidence suggests
                  </h3>
                </div>

                <span>
                  {comparisonExplanation
                    ? `${comparisonExplanation.model} · Explanation only`
                    : 'Explanation only'}
                </span>
              </div>

              <div className="comparison-ai-content">
                <p>
                  {comparisonExplanation
                    ? comparisonExplanation.explanation
                    : 'No grounded comparison explanation is currently available.'}
                </p>

                <div className="comparison-ai-tradeoffs">
                  <div>
                    <span>
                      Evidence focus
                    </span>

                    <strong>
                      Compare required skills, experience,
                      responsibilities and supporting evidence
                    </strong>
                  </div>

                  <div>
                    <span>
                      Key trade-off
                    </span>

                    <strong>
                      Technical skill gaps may require
                      additional validation
                    </strong>
                  </div>

                  <div>
                    <span>
                      Review consideration
                    </span>

                    <strong>
                      Validate missing skills during the
                      interview process
                    </strong>
                  </div>
                </div>
              </div>
            </section>

            <div className="comparison-responsible-note">
              <strong>
                Recruiter decision required
              </strong>

              <span>
                TalentMatch compares evidence and explains the matching
                results. It does not make hiring decisions.
              </span>
            </div>
          </>
        )}
    </div>
  )
}

export default CandidateComparison