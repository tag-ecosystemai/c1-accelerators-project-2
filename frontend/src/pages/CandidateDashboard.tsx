import { useEffect, useMemo, useState } from 'react'
import {
  getCandidates,
  getJobProfile,
  type CandidateResultResponse,
  type JobProfileResponse,
} from '../services/api'

interface CandidateDashboardProps {
  jobId: number | null
  onCandidateSelect: (candidateId: string) => void
}

interface DashboardCandidate {
  id: string
  rank: number | null
  name: string
  score: number | null
  requiredSkills: string
  missingSkills: string[]
  status: string
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

function getMissingSkills(
  candidate: CandidateResultResponse,
): string[] {
  const skillMatches = candidate.match_result.skill_matches

  if (!Array.isArray(skillMatches)) {
    return []
  }

  return skillMatches
    .filter((skillMatch) => {
      if (!skillMatch || typeof skillMatch !== 'object') {
        return false
      }

      return (
        (skillMatch as Record<string, unknown>).status ===
        'missing'
      )
    })
    .map((skillMatch) => {
      if (!skillMatch || typeof skillMatch !== 'object') {
        return ''
      }

      const skill = (
        skillMatch as Record<string, unknown>
      ).skill

      if (!skill || typeof skill !== 'object') {
        return ''
      }

      const name = (
        skill as Record<string, unknown>
      ).name

      return typeof name === 'string' ? name : ''
    })
    .filter(Boolean)
}

function mapCandidate(
  candidate: CandidateResultResponse,
): DashboardCandidate {
  const coverage = candidate.required_skill_coverage

  return {
    id: String(candidate.candidate.id),
    rank: candidate.rank,
    name: getCandidateName(candidate),
    score: candidate.overall_score,
    requiredSkills: coverage
      ? `${coverage.matched} / ${coverage.total}`
      : '0 / 0',
    missingSkills: getMissingSkills(candidate),
    status:
      candidate.candidate.processing_status === 'completed'
        ? 'Processed'
        : candidate.candidate.processing_status,
  }
}

function formatExperience(
  profile: JobProfileResponse,
): string {
  if (profile.minimum_experience_years === null) {
    return ''
  }

  return `${profile.minimum_experience_years}+ years`
}

function formatScore(
  score: number | null,
): string {
  return score === null
    ? '—'
    : `${score.toFixed(2)}%`
}

function CandidateDashboard({
  jobId,
  onCandidateSelect,
}: CandidateDashboardProps) {
  const [candidates, setCandidates] = useState<
    DashboardCandidate[]
  >([])

  const [jobProfile, setJobProfile] =
    useState<JobProfileResponse | null>(null)

  const [search, setSearch] = useState('')
  const [minimumScore, setMinimumScore] = useState('')
  const [requiredCoverage, setRequiredCoverage] =
    useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (jobId === null) {
      return
    }

    let cancelled = false

    const loadDashboard = async () => {
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
          candidatesResponse.candidates.map(mapCandidate),
        )
      } catch (err) {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load screening results.',
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadDashboard()

    return () => {
      cancelled = true
    }
  }, [jobId])

  const filteredCandidates = useMemo(() => {
    return candidates.filter((candidate) => {
      const searchValue = search.toLowerCase().trim()

      const matchesSearch =
        !searchValue ||
        candidate.name
          .toLowerCase()
          .includes(searchValue) ||
        candidate.id
          .toLowerCase()
          .includes(searchValue)

      const matchesScore =
        !minimumScore ||
        (candidate.score !== null &&
          candidate.score >= Number(minimumScore))

      const [
        matched,
        total,
      ] = candidate.requiredSkills
        .split('/')
        .map((value) => Number(value.trim()))

      const coverage =
        total > 0
          ? (matched / total) * 100
          : 0

      const matchesCoverage =
        !requiredCoverage ||
        coverage >= Number(requiredCoverage)

      return (
        matchesSearch &&
        matchesScore &&
        matchesCoverage
      )
    })
  }, [
    candidates,
    search,
    minimumScore,
    requiredCoverage,
  ])

  return (
    <div className="dashboard-page">
      <section className="dashboard-intro">
        <div>
          <span className="page-eyebrow">
            Screening results
          </span>

          <h2>Review the shortlist.</h2>

          <p>
            Candidates are ranked by the matching engine. Use
            the evidence and score breakdown to decide who
            deserves a closer review.
          </p>
        </div>

        <div className="dashboard-result-count">
          <strong>
            {filteredCandidates.length}
          </strong>

          <span>
            {filteredCandidates.length === 1
              ? 'candidate shown'
              : 'candidates shown'}
          </span>
        </div>
      </section>

      <section className="dashboard-requirements">
        <div className="dashboard-requirement-intro">
          <span>Screening against</span>

          <strong>
            {jobProfile?.title ?? 'Loading role...'}
          </strong>
        </div>

        <div className="dashboard-requirement-group">
          <span>Required</span>

          <div>
            {jobProfile?.required_skills.map(
              (skill) => (
                <span
                  key={skill.normalized_name}
                  className="dashboard-skill required"
                >
                  {skill.name}
                </span>
              ),
            )}
          </div>
        </div>

        <div className="dashboard-requirement-group">
          <span>Preferred</span>

          <div>
            {jobProfile?.preferred_skills.map(
              (skill) => (
                <span
                  key={skill.normalized_name}
                  className="dashboard-skill preferred"
                >
                  {skill.name}
                </span>
              ),
            )}
          </div>
        </div>

        <div className="dashboard-requirement-meta">
          {jobProfile &&
            formatExperience(jobProfile) && (
              <span>
                {formatExperience(jobProfile)}
              </span>
            )}

          {jobProfile &&
            jobProfile.education_requirements
              .length > 0 && (
              <span>
                {jobProfile.education_requirements.join(
                  ', ',
                )}
              </span>
            )}
        </div>
      </section>

      <section className="dashboard-toolbar">
        <div className="dashboard-search">
          <span
            className="dashboard-search-icon"
            aria-hidden="true"
          >
            ⌕
          </span>

          <input
            type="search"
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search candidates..."
            aria-label="Search candidates"
          />
        </div>

        <div className="dashboard-filter">
          <label htmlFor="minimum-score">
            Minimum score
          </label>

          <select
            id="minimum-score"
            value={minimumScore}
            onChange={(event) =>
              setMinimumScore(event.target.value)
            }
          >
            <option value="">Any score</option>
            <option value="90">90+</option>
            <option value="80">80+</option>
            <option value="70">70+</option>
          </select>
        </div>

        <div className="dashboard-filter">
          <label htmlFor="required-coverage">
            Required coverage
          </label>

          <select
            id="required-coverage"
            value={requiredCoverage}
            onChange={(event) =>
              setRequiredCoverage(event.target.value)
            }
          >
            <option value="">Any coverage</option>
            <option value="100">100%</option>
            <option value="75">75%+</option>
            <option value="50">50%+</option>
          </select>
        </div>
      </section>

      <section className="dashboard-candidates">
        <div className="dashboard-table-header">
          <div>
            <span className="dashboard-table-eyebrow">
              Candidate ranking
            </span>

            <h3>Best matches</h3>
          </div>

          <span className="dashboard-ranking-note">
            Ranking determined by matching engine
          </span>
        </div>

        <div className="dashboard-table">
          <div className="dashboard-table-head">
            <span>Rank</span>
            <span>Candidate</span>
            <span>Fit</span>
            <span>Required skills</span>
            <span>Gaps</span>
            <span>Status</span>
            <span />
          </div>

          {loading && (
            <div className="dashboard-empty">
              <strong>
                Loading screening results...
              </strong>

              <span>
                Retrieving candidates from the matching
                engine.
              </span>
            </div>
          )}

          {!loading &&
            !error &&
            filteredCandidates.map(
              (candidate) => (
                <button
                  key={candidate.id}
                  type="button"
                  className="dashboard-candidate-row"
                  onClick={() =>
                    onCandidateSelect(
                      candidate.id,
                    )
                  }
                >
                  <span className="dashboard-rank">
                    {candidate.rank !== null
                      ? String(
                          candidate.rank,
                        ).padStart(2, '0')
                      : '—'}
                  </span>

                  <span className="dashboard-candidate">
                    <span className="dashboard-avatar">
                      {candidate.name
                        .split(' ')
                        .map(
                          (name) =>
                            name[0],
                        )
                        .join('')}
                    </span>

                    <span>
                      <strong>
                        {candidate.name}
                      </strong>

                      <small>
                        {candidate.id}
                      </small>
                    </span>
                  </span>

                  <span className="dashboard-fit">
                    <strong>
                      {formatScore(
                        candidate.score,
                      )}
                    </strong>

                    <span>
                      {candidate.score === null
                        ? 'Pending'
                        : candidate.score >= 85
                          ? 'Strong match'
                          : candidate.score >= 75
                            ? 'Good match'
                            : 'Review'}
                    </span>
                  </span>

                  <span className="dashboard-coverage">
                    <strong>
                      {candidate.requiredSkills}
                    </strong>

                    <span>required</span>
                  </span>

                  <span className="dashboard-gaps">
                    {candidate.missingSkills
                      .length === 0 ? (
                      <span className="dashboard-no-gap">
                        None
                      </span>
                    ) : (
                      candidate.missingSkills.map(
                        (skill) => (
                          <span key={skill}>
                            {skill}
                          </span>
                        ),
                      )
                    )}
                  </span>

                  <span className="dashboard-status">
                    <i />

                    {candidate.status}
                  </span>

                  <span
                    className="dashboard-arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>
                </button>
              ),
            )}

          {!loading && error && (
            <div className="dashboard-empty">
              <strong>
                Unable to load screening results.
              </strong>

              <span>{error}</span>
            </div>
          )}

          {!loading &&
            !error &&
            filteredCandidates.length === 0 && (
              <div className="dashboard-empty">
                <strong>
                  No candidates match these filters.
                </strong>

                <span>
                  Try widening your search criteria.
                </span>
              </div>
            )}
        </div>
      </section>

      <div className="dashboard-footnote">
        <span>Human review required</span>

        <p>
          TalentMatch provides matching evidence and
          rankings. Final hiring decisions remain with the
          recruiter.
        </p>
      </div>
    </div>
  )
}

export default CandidateDashboard