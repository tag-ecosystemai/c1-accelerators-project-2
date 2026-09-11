const mockCandidate = {
  name: 'Amara Okafor',
  email: 'amara.okafor@example.com',
  score: 91,
  requiredSkillCoverage: {
    matched: 4,
    total: 4,
    percentage: 100,
  },
  scoreBreakdown: {
    requiredSkills: 38,
    relevantExperience: 23,
    responsibilitiesAlignment: 14,
    education: 9,
    preferredSkills: 7,
  },
  skills: [
    {
      name: 'Python',
      status: 'Matched',
      score: 1,
      evidence:
        'Built and maintained Python backend services for internal applications.',
    },
    {
      name: 'FastAPI',
      status: 'Matched',
      score: 1,
      evidence:
        'Developed REST APIs using FastAPI for a production web application.',
    },
    {
      name: 'SQL',
      status: 'Matched',
      score: 1,
      evidence:
        'Designed SQL queries and worked with PostgreSQL databases.',
    },
    {
      name: 'REST APIs',
      status: 'Matched',
      score: 1,
      evidence:
        'Designed and integrated REST APIs across multiple backend projects.',
    },
    {
      name: 'Docker',
      status: 'Partial',
      score: 0.6,
      evidence:
        'Used Docker for local development and application deployment.',
    },
    {
      name: 'AWS',
      status: 'Missing',
      score: 0,
      evidence: 'No evidence found in the submitted resume.',
    },
  ],
  explanation:
    'Amara Okafor is a strong match for this role based on the evidence found in the submitted resume. The candidate demonstrates all four required technical skills, with direct experience in Python, FastAPI, SQL, and REST API development. Relevant backend experience and strong responsibility alignment further support the high overall fit score. AWS was not found in the resume and therefore does not contribute to the candidate match.',
}

const mockCandidates = {
  'candidate-001': mockCandidate,
  'candidate-002': {
    ...mockCandidate,
    name: 'Daniel Okoro',
    email: 'daniel.okoro@example.com',
    score: 84,
  },
  'candidate-003': {
    ...mockCandidate,
    name: 'Chinonso Eze',
    email: 'chinonso.eze@example.com',
    score: 76,
  },
}

interface CandidateReviewProps {
  candidateId: string | null
  onBack: () => void
}

function CandidateReview({
  candidateId,
  onBack,
}: CandidateReviewProps) {
  const candidate = candidateId
    ? mockCandidates[candidateId as keyof typeof mockCandidates]
    : mockCandidate

  return (
    <div className="candidate-review">
      {/* Candidate Header */}
      <section className="candidate-review-header">
        <div className="candidate-review-identity">
          <span className="eyebrow">Candidate Review</span>

          <h1>{candidate.name}</h1>

          <div className="candidate-meta">
            <span>{candidate.email}</span>
            <span className="candidate-meta-divider">•</span>
            <span>
              candidate-{candidateId?.split('-').pop() ?? '001'}
            </span>
          </div>
        </div>

        <div className="candidate-review-result">
          <button
            type="button"
            className="secondary-button"
            onClick={onBack}
          >
            Back to Candidates
          </button>
          <div className="candidate-review-status">
            <span className="status-dot" />
            Processed
          </div>

          <div className="candidate-fit">
            <span>Overall Fit</span>
            <strong>{candidate.score}%</strong>
          </div>

          <div className="candidate-coverage">
            <span>Required Skills</span>
            <strong>
              {candidate.requiredSkillCoverage.matched}/
              {candidate.requiredSkillCoverage.total}
            </strong>
          </div>
        </div>
      </section>

      {/* Match Summary */}
      <section className="review-summary">
        <div className="summary-card">
          <span className="summary-label">Required Skills</span>

          <strong>
            {candidate.requiredSkillCoverage.matched} /{' '}
            {candidate.requiredSkillCoverage.total}
          </strong>

          <span>
            {candidate.requiredSkillCoverage.percentage}% coverage
          </span>
        </div>

        <div className="summary-card">
          <span className="summary-label">Matched Skills</span>

          <strong>
            {
              candidate.skills.filter(
                (skill) => skill.status === 'Matched',
              ).length
            }
          </strong>

          <span>Skills with supporting evidence</span>
        </div>

        <div className="summary-card">
          <span className="summary-label">Skill Gaps</span>

          <strong>
            {
              candidate.skills.filter(
                (skill) =>
                  skill.status === 'Missing' ||
                  skill.status === 'Partial',
              ).length
            }
          </strong>

          <span>Skills requiring further review</span>
        </div>
      </section>

      {/* Score Breakdown */}
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Scoring</span>

            <h2>Score Breakdown</h2>

            <p>
              The deterministic matching engine calculated the
              candidate's overall fit.
            </p>
          </div>
        </div>

        <div className="score-breakdown">
          <div className="score-row">
            <div className="score-row-label">
              <span>Required Skills</span>
              <strong>
                {candidate.scoreBreakdown.requiredSkills}/40
              </strong>
            </div>

            <div className="score-track">
              <div
                className="score-fill"
                style={{
                  width: `${(candidate.scoreBreakdown.requiredSkills / 40) * 100}%`,
                }}
              />
            </div>
          </div>

          <div className="score-row">
            <div className="score-row-label">
              <span>Relevant Experience</span>
              <strong>
                {candidate.scoreBreakdown.relevantExperience}/25
              </strong>
            </div>

            <div className="score-track">
              <div
                className="score-fill"
                style={{
                  width: `${(candidate.scoreBreakdown.relevantExperience / 25) * 100}%`,
                }}
              />
            </div>
          </div>

          <div className="score-row">
            <div className="score-row-label">
              <span>Responsibilities Alignment</span>
              <strong>
                {candidate.scoreBreakdown.responsibilitiesAlignment}/15
              </strong>
            </div>

            <div className="score-track">
              <div
                className="score-fill"
                style={{
                  width: `${(candidate.scoreBreakdown.responsibilitiesAlignment / 15) * 100}%`,
                }}
              />
            </div>
          </div>

          <div className="score-row">
            <div className="score-row-label">
              <span>Education</span>
              <strong>
                {candidate.scoreBreakdown.education}/10
              </strong>
            </div>

            <div className="score-track">
              <div
                className="score-fill"
                style={{
                  width: `${(candidate.scoreBreakdown.education / 10) * 100}%`,
                }}
              />
            </div>
          </div>

          <div className="score-row">
            <div className="score-row-label">
              <span>Preferred Skills</span>
              <strong>
                {candidate.scoreBreakdown.preferredSkills}/10
              </strong>
            </div>

            <div className="score-track">
              <div
                className="score-fill"
                style={{
                  width: `${(candidate.scoreBreakdown.preferredSkills / 10) * 100}%`,
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Skill Analysis */}
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Skill Analysis</span>

            <h2>Skills & Evidence</h2>

            <p>
              Each match is supported by evidence from the candidate's
              submitted resume.
            </p>
          </div>
        </div>

        <div className="skill-analysis">
          {candidate.skills.map((skill) => (
            <div
              className="skill-analysis-row"
              key={skill.name}
            >
              <div className="skill-analysis-header">
                <div className="skill-analysis-name">
                  <strong>{skill.name}</strong>

                  <span
                    className={`skill-status ${skill.status.toLowerCase()}`}
                  >
                    {skill.status}
                  </span>
                </div>
              </div>

              <div className="skill-evidence">
                <span className="evidence-label">
                  Resume evidence
                </span>

                <p>{skill.evidence}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
      {/* Skill Gaps */}
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Skill Gaps</span>

            <h2>Areas for Further Review</h2>

            <p>
              Skills that are partially supported or not found in the
              candidate's submitted resume.
            </p>
          </div>
        </div>

        <div className="skill-gaps">
          {candidate.skills
            .filter(
              (skill) =>
                skill.status === 'Partial' ||
                skill.status === 'Missing',
            )
            .map((skill) => (
              <div className="skill-gap-row" key={skill.name}>
                <div className="skill-gap-header">
                  <strong>{skill.name}</strong>

                  <span
                    className={`skill-status ${skill.status.toLowerCase()}`}
                  >
                    {skill.status}
                  </span>
                </div>

                <p>{skill.evidence}</p>
              </div>
            ))}
        </div>
      </section>
      {/* LLM Explanation */}
      <section className="panel explanation-panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Explanation</span>

            <h2>Why this candidate matched</h2>

            <p>
              A grounded explanation of the matching results and
              supporting resume evidence.
            </p>
          </div>

          <span className="status-badge">
            LLM Explanation
          </span>
        </div>

        <div className="explanation-content">
          <div className="explanation-notice">
            <strong>Evidence-based explanation</strong>

            <span>
              The LLM explains the matching engine's results. It does not
              determine the candidate's score or ranking.
            </span>
          </div>

          <p>{candidate.explanation}</p>
        </div>
      </section>
    </div>
  )
}

export default CandidateReview
