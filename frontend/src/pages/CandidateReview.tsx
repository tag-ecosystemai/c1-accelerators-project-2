import { useEffect, useState } from 'react'
import {
  getCandidate,
  getCandidateExplanation,
  type CandidateResultResponse,
  type CandidateExplanationResponse,
} from '../services/api'

interface CandidateReviewProps {
  jobId: number | null
  candidateId: string | null
  onBack: () => void
}

interface ReviewSkill {
  name: string
  status: 'Matched' | 'Partial' | 'Missing'
  score: number
  evidence: string
}

const scoreItems = [
  {
    key: 'requiredSkills',
    label: 'Required Skills',
    maximum: 40,
  },
  {
    key: 'relevantExperience',
    label: 'Relevant Experience',
    maximum: 25,
  },
  {
    key: 'responsibilitiesAlignment',
    label: 'Responsibilities Alignment',
    maximum: 15,
  },
  {
    key: 'education',
    label: 'Education',
    maximum: 10,
  },
  {
    key: 'preferredSkills',
    label: 'Preferred Skills',
    maximum: 10,
  },
] as const

function getCandidateName(
  result: CandidateResultResponse,
): string {
  const name = result.candidate.profile.name

  if (typeof name === 'string' && name.trim()) {
    return name
  }

  return result.candidate.source_filename
}

function getCandidateEmail(
  result: CandidateResultResponse,
): string | null {
  const email = result.candidate.profile.email

  return typeof email === 'string' && email.trim()
    ? email
    : null
}

function getSkillMatches(
  result: CandidateResultResponse,
): ReviewSkill[] {
  const matches = result.match_result.skill_matches

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
      const skillMatch =
        match as Record<string, unknown>

      const skill =
        skillMatch.skill &&
        typeof skillMatch.skill === 'object'
          ? (skillMatch.skill as Record<string, unknown>)
          : null

      const name =
        skill && typeof skill.name === 'string'
          ? skill.name
          : 'Unknown skill'

      const status =
        skillMatch.status === 'matched'
          ? 'Matched'
          : skillMatch.status === 'partial'
            ? 'Partial'
            : 'Missing'

      const score =
        typeof skillMatch.match_score === 'number'
          ? skillMatch.match_score
          : 0

      const evidence = Array.isArray(
        skillMatch.evidence,
      )
        ? skillMatch.evidence
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
            .join(' ')
        : ''

      return {
        name,
        status,
        score,
        evidence:
          evidence ||
          'No evidence found in the submitted resume.',
      }
    })
}

function getScoreValue(
  result: CandidateResultResponse,
  key: string,
): number {
  const breakdown = result.score_breakdown
  const value = breakdown[key]

  return typeof value === 'number'
    ? value
    : 0
}

function CandidateReview({
  jobId,
  candidateId,
  onBack,
}: CandidateReviewProps) {
  const [candidate, setCandidate] =
    useState<CandidateResultResponse | null>(null)

  const [explanation, setExplanation] =
    useState<CandidateExplanationResponse | null>(
      null,
    )

  const [loading, setLoading] = useState(true)
  const [explanationLoading, setExplanationLoading] =
    useState(true)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    if (
      jobId === null ||
      candidateId === null
    ) {
      return
    }

    let cancelled = false

    const loadCandidate = async () => {
      setLoading(true)
      setError(null)

      try {
        const result = await getCandidate(
          jobId,
          Number(candidateId),
        )

        if (cancelled) {
          return
        }

        setCandidate(result)
      } catch (err) {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load candidate.',
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadCandidate()

    return () => {
      cancelled = true
    }
  }, [jobId, candidateId])

  useEffect(() => {
    if (
      jobId === null ||
      candidateId === null
    ) {
      return
    }

    let cancelled = false

    const loadExplanation = async () => {
      setExplanationLoading(true)

      try {
        const result =
          await getCandidateExplanation(
            jobId,
            Number(candidateId),
          )

        if (cancelled) {
          return
        }

        setExplanation(result)
      } catch {
        if (cancelled) {
          return
        }

        setExplanation(null)
      } finally {
        if (!cancelled) {
          setExplanationLoading(false)
        }
      }
    }

    void loadExplanation()

    return () => {
      cancelled = true
    }
  }, [jobId, candidateId])

  if (loading) {
    return (
      <div className="review-page">
        <button
          type="button"
          className="review-back-button"
          onClick={onBack}
        >
          <span aria-hidden="true">←</span>
          Back to candidates
        </button>

        <div className="dashboard-empty">
          <strong>
            Loading candidate...
          </strong>

          <span>
            Retrieving the candidate's matching results.
          </span>
        </div>
      </div>
    )
  }

  if (error || !candidate) {
    return (
      <div className="review-page">
        <button
          type="button"
          className="review-back-button"
          onClick={onBack}
        >
          <span aria-hidden="true">←</span>
          Back to candidates
        </button>

        <div className="dashboard-empty">
          <strong>
            Unable to load candidate.
          </strong>

          <span>
            {error ??
              'Candidate data is unavailable.'}
          </span>
        </div>
      </div>
    )
  }

  const name = getCandidateName(candidate)
  const email = getCandidateEmail(candidate)
  const skills = getSkillMatches(candidate)

  const matchedSkills = skills.filter(
    (skill) => skill.status === 'Matched',
  )

  const partialSkills = skills.filter(
    (skill) => skill.status === 'Partial',
  )

  const missingSkills = skills.filter(
    (skill) => skill.status === 'Missing',
  )

  const score = candidate.overall_score
  const coverage =
    candidate.required_skill_coverage

  const scoreLabel =
    score === null
      ? 'Pending'
      : score >= 85
        ? 'Strong match'
        : score >= 75
          ? 'Good match'
          : 'Review'

  return (
    <div className="review-page">
      <button
        type="button"
        className="review-back-button"
        onClick={onBack}
      >
        <span aria-hidden="true">←</span>
        Back to candidates
      </button>

      <section className="review-candidate-header">
        <div className="review-candidate-identity">
          <div className="review-large-avatar">
            {name
              .split(' ')
              .map((part) => part[0])
              .join('')}
          </div>

          <div>
            <span className="page-eyebrow">
              Candidate review
            </span>

            <h2>{name}</h2>

            <div className="review-candidate-meta">
              {email && (
                <span>{email}</span>
              )}

              <span>
                candidate-
                {String(
                  candidate.candidate.id,
                ).padStart(3, '0')}
              </span>

              <span className="review-processed">
                <i />
                {candidate.candidate.processing_status}
              </span>
            </div>
          </div>
        </div>

        <div className="review-overall">
          <span>Overall fit</span>

          <strong>
            {score !== null
              ? `${score}%`
              : '—'}
          </strong>

          <small>{scoreLabel}</small>
        </div>
      </section>

      <section className="review-summary-grid">
        <div className="review-summary-card primary">
          <span>
            Required skill coverage
          </span>

          <strong>
            {coverage
              ? `${coverage.matched}/${coverage.total}`
              : '—'}
          </strong>

          <div className="review-progress">
            <span
              style={{
                width: `${
                  coverage?.percentage ?? 0
                }%`,
              }}
            />
          </div>

          <small>
            {coverage
              ? `${coverage.percentage}% of required skills matched`
              : 'Coverage unavailable'}
          </small>
        </div>

        <div className="review-summary-card">
          <span>Matched skills</span>
          <strong>
            {matchedSkills.length}
          </strong>
          <small>
            Direct evidence found
          </small>
        </div>

        <div className="review-summary-card">
          <span>Partial matches</span>
          <strong>
            {partialSkills.length}
          </strong>
          <small>
            Some supporting evidence
          </small>
        </div>

        <div className="review-summary-card attention">
          <span>Skill gaps</span>
          <strong>
            {missingSkills.length}
          </strong>
          <small>
            Not found in resume
          </small>
        </div>
      </section>

      <div className="review-main-grid">
        <section className="review-panel review-score-panel">
          <div className="review-panel-header">
            <div>
              <span className="review-panel-eyebrow">
                Deterministic result
              </span>

              <h3>Score breakdown</h3>
            </div>

            <span className="review-panel-weight">
              100 points
            </span>
          </div>

          <p className="review-panel-description">
            The matching engine calculates the score
            from five predefined dimensions. The LLM
            does not determine this result.
          </p>

          <div className="review-score-list">
            {scoreItems.map((item) => {
              const value =
                getScoreValue(
                  candidate,
                  item.key,
                )

              const percentage =
                (value / item.maximum) * 100

              return (
                <div
                  key={item.key}
                  className="review-score-item"
                >
                  <div className="review-score-label">
                    <span>
                      {item.label}
                    </span>

                    <strong>
                      {value}/{item.maximum}
                    </strong>
                  </div>

                  <div className="review-score-track">
                    <span
                      style={{
                        width: `${percentage}%`,
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </section>

        <section className="review-panel review-signal-panel">
          <div className="review-panel-header">
            <div>
              <span className="review-panel-eyebrow">
                Recruiter signal
              </span>

              <h3>What stands out</h3>
            </div>
          </div>

          {coverage &&
            coverage.matched ===
              coverage.total &&
            coverage.total > 0 && (
              <div className="review-signal">
                <span className="review-signal-icon">
                  +
                </span>

                <div>
                  <strong>
                    All required skills matched
                  </strong>

                  <p>
                    Direct evidence was found
                    for all required skills
                    evaluated by the matching
                    engine.
                  </p>
                </div>
              </div>
            )}

          {missingSkills.length > 0 && (
            <div className="review-signal peach">
              <span className="review-signal-icon">
                !
              </span>

              <div>
                <strong>
                  {missingSkills.length === 1
                    ? `${missingSkills[0].name} is a gap`
                    : `${missingSkills.length} skill gaps identified`}
                </strong>

                <p>
                  No supporting evidence was
                  found for
                  {missingSkills.length === 1
                    ? ` ${missingSkills[0].name}.`
                    : ' some evaluated skills.'}
                </p>
              </div>
            </div>
          )}

          <div className="review-signal neutral">
            <span className="review-signal-icon">
              i
            </span>

            <div>
              <strong>
                Human review remains essential
              </strong>

              <p>
                A missing signal means no
                evidence was found, not that the
                candidate definitely lacks the
                skill.
              </p>
            </div>
          </div>
        </section>
      </div>

      <section className="review-panel review-skills-panel">
        <div className="review-panel-header">
          <div>
            <span className="review-panel-eyebrow">
              Evidence
            </span>

            <h3>Skill analysis</h3>

            <p className="review-panel-description">
              Review the match status, supporting resume
              evidence, and contribution of each evaluated
              skill.
            </p>
          </div>

          <span className="review-evidence-count">
            {skills.length} skills evaluated
          </span>
        </div>

        <div className="review-skill-legend">
          <span>
            <i className="matched" />
            Matched
          </span>

          <span>
            <i className="partial" />
            Partial
          </span>

          <span>
            <i className="missing" />
            Missing
          </span>
        </div>

        <div className="review-skills-list">
          {skills.map((skill) => {
            const matchPercentage =
              Math.round(
                skill.score * 100,
              )

            return (
              <article
                key={skill.name}
                className={`review-skill-row ${skill.status.toLowerCase()}`}
              >
                <div className="review-skill-name">
                  <span
                    className={`review-skill-status ${skill.status.toLowerCase()}`}
                    aria-label={`${skill.status} skill`}
                  >
                    {skill.status ===
                    'Matched'
                      ? '✓'
                      : skill.status ===
                          'Partial'
                        ? '~'
                        : '—'}
                  </span>

                  <div>
                    <strong>
                      {skill.name}
                    </strong>

                    <span className="review-skill-status-label">
                      {skill.status}
                    </span>
                  </div>
                </div>

                <div className="review-skill-evidence">
                  <span>
                    Resume evidence
                  </span>

                  <p>
                    {skill.evidence}
                  </p>
                </div>

                <div className="review-skill-score">
                  <strong>
                    {matchPercentage}%
                  </strong>

                  <span>match</span>

                  <div
                    className="review-skill-score-track"
                    aria-hidden="true"
                  >
                    <span
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            matchPercentage,
                          ),
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </article>
            )
          })}

          {skills.length === 0 && (
            <div className="review-skill-empty">
              <strong>
                No skills were evaluated.
              </strong>

              <span>
                Skill analysis is unavailable for
                this candidate.
              </span>
            </div>
          )}
        </div>
      </section>

      <section className="review-gap-panel">
        <div>
          <span className="review-panel-eyebrow">
            Attention
          </span>

          <h3>Skill gaps</h3>

          <p>
            These skills did not receive full evidence
            support from the submitted resume.
          </p>
        </div>

        <div className="review-gap-list">
          {skills
            .filter(
              (skill) =>
                skill.status !== 'Matched',
            )
            .map((skill) => (
              <div
                key={skill.name}
                className="review-gap-item"
              >
                <strong>
                  {skill.name}
                </strong>

                <span>
                  {skill.status}
                </span>
              </div>
            ))}
        </div>
      </section>

      <section className="review-panel review-explanation-panel">
        <div className="review-explanation-header">
          <div>
            <span className="review-panel-eyebrow">
              Grounded explanation
            </span>

            <h3>
              Why this candidate matches
            </h3>
          </div>

          <span className="review-llm-label">
            {explanation
              ? `Groq · ${explanation.model}`
              : 'Groq · Explanation only'}
          </span>
        </div>

        <div className="review-explanation-body">
          <div className="review-explanation-quote">
            <span>“</span>
          </div>

          <p>
            {explanationLoading
              ? 'Generating grounded explanation...'
              : explanation?.explanation ??
                'No grounded explanation is currently available.'}
          </p>
        </div>

        <div className="review-explanation-notice">
          <strong>Important:</strong>

          <span>
            This explanation is generated from the
            matching engine's results and supporting
            evidence. The LLM does not score, rank or
            select candidates.
          </span>
        </div>
      </section>
    </div>
  )
}

export default CandidateReview