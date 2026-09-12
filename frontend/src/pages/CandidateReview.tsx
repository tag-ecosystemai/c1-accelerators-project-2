interface CandidateReviewProps {
  candidateId: string | null
  onBack: () => void
}

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

const mockCandidates: Record<string, typeof mockCandidate> = {
  'candidate-001': mockCandidate,
  'candidate-002': {
    ...mockCandidate,
    name: 'Daniel Mensah',
    email: 'daniel.mensah@example.com',
    score: 84,
  },
  'candidate-003': {
    ...mockCandidate,
    name: 'Chinonso Eze',
    email: 'chinonso.eze@example.com',
    score: 76,
  },
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

function CandidateReview({
  candidateId,
  onBack,
}: CandidateReviewProps) {
  const candidate =
    (candidateId && mockCandidates[candidateId]) || mockCandidate

  const matchedSkills = candidate.skills.filter(
    (skill) => skill.status === 'Matched',
  )

  const partialSkills = candidate.skills.filter(
    (skill) => skill.status === 'Partial',
  )

  const missingSkills = candidate.skills.filter(
    (skill) => skill.status === 'Missing',
  )

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
            {candidate.name
              .split(' ')
              .map((name) => name[0])
              .join('')}
          </div>

          <div>
            <span className="page-eyebrow">Candidate review</span>

            <h2>{candidate.name}</h2>

            <div className="review-candidate-meta">
              <span>{candidate.email}</span>
              <span>candidate-001</span>
              <span className="review-processed">
                <i />
                Processed
              </span>
            </div>
          </div>
        </div>

        <div className="review-overall">
          <span>Overall fit</span>
          <strong>{candidate.score}%</strong>
          <small>Strong match</small>
        </div>
      </section>

      <section className="review-summary-grid">
        <div className="review-summary-card primary">
          <span>Required skill coverage</span>

          <strong>
            {candidate.requiredSkillCoverage.matched}/
            {candidate.requiredSkillCoverage.total}
          </strong>

          <div className="review-progress">
            <span
              style={{
                width: `${candidate.requiredSkillCoverage.percentage}%`,
              }}
            />
          </div>

          <small>
            {candidate.requiredSkillCoverage.percentage}% of required skills
            matched
          </small>
        </div>

        <div className="review-summary-card">
          <span>Matched skills</span>
          <strong>{matchedSkills.length}</strong>
          <small>Direct evidence found</small>
        </div>

        <div className="review-summary-card">
          <span>Partial matches</span>
          <strong>{partialSkills.length}</strong>
          <small>Some supporting evidence</small>
        </div>

        <div className="review-summary-card attention">
          <span>Skill gaps</span>
          <strong>{missingSkills.length}</strong>
          <small>Not found in resume</small>
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

            <span className="review-panel-weight">100 points</span>
          </div>

          <p className="review-panel-description">
            The matching engine calculates the score from five predefined
            dimensions. The LLM does not determine this result.
          </p>

          <div className="review-score-list">
            {scoreItems.map((item) => {
              const value = candidate.scoreBreakdown[item.key]
              const percentage = (value / item.maximum) * 100

              return (
                <div key={item.key} className="review-score-item">
                  <div className="review-score-label">
                    <span>{item.label}</span>
                    <strong>
                      {value}/{item.maximum}
                    </strong>
                  </div>

                  <div className="review-score-track">
                    <span style={{ width: `${percentage}%` }} />
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

          <div className="review-signal">
            <span className="review-signal-icon">+</span>

            <div>
              <strong>All required skills matched</strong>
              <p>
                Direct evidence was found for Python, FastAPI, SQL and REST
                APIs.
              </p>
            </div>
          </div>

          <div className="review-signal peach">
            <span className="review-signal-icon">!</span>

            <div>
              <strong>AWS is a gap</strong>
              <p>
                No evidence of AWS experience was found in the submitted
                resume.
              </p>
            </div>
          </div>

          <div className="review-signal neutral">
            <span className="review-signal-icon">i</span>

            <div>
              <strong>Human review remains essential</strong>
              <p>
                A missing signal means no evidence was found, not that the
                candidate definitely lacks the skill.
              </p>
            </div>
          </div>
        </section>
      </div>

      <section className="review-panel review-skills-panel">
        <div className="review-panel-header">
          <div>
            <span className="review-panel-eyebrow">Evidence</span>
            <h3>Skill analysis</h3>
          </div>

          <span className="review-evidence-count">
            {candidate.skills.length} skills evaluated
          </span>
        </div>

        <div className="review-skills-list">
          {candidate.skills.map((skill) => (
            <article key={skill.name} className="review-skill-row">
              <div className="review-skill-name">
                <span
                  className={`review-skill-status ${skill.status.toLowerCase()}`}
                >
                  {skill.status === 'Matched'
                    ? '✓'
                    : skill.status === 'Partial'
                      ? '~'
                      : '—'}
                </span>

                <div>
                  <strong>{skill.name}</strong>
                  <small>{skill.status}</small>
                </div>
              </div>

              <div className="review-skill-evidence">
                <span>Resume evidence</span>
                <p>{skill.evidence}</p>
              </div>

              <div className="review-skill-score">
                <strong>{Math.round(skill.score * 100)}%</strong>
                <span>match</span>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="review-gap-panel">
        <div>
          <span className="review-panel-eyebrow">Attention</span>
          <h3>Skill gaps</h3>
          <p>
            These skills did not receive full evidence support from the
            submitted resume.
          </p>
        </div>

        <div className="review-gap-list">
          {candidate.skills
            .filter((skill) => skill.status !== 'Matched')
            .map((skill) => (
              <div key={skill.name} className="review-gap-item">
                <strong>{skill.name}</strong>
                <span>{skill.status}</span>
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
            <h3>Why this candidate matches</h3>
          </div>

          <span className="review-llm-label">
            Groq · Explanation only
          </span>
        </div>

        <div className="review-explanation-body">
          <div className="review-explanation-quote">
            <span>“</span>
          </div>

          <p>{candidate.explanation}</p>
        </div>

        <div className="review-explanation-notice">
          <strong>Important:</strong>

          <span>
            This explanation is generated from the matching engine's results
            and supporting evidence. The LLM does not score, rank or select
            candidates.
          </span>
        </div>
      </section>
    </div>
  )
}

export default CandidateReview