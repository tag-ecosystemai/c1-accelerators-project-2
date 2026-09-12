import { useState } from 'react'

interface CandidateComparisonProps {
  onBack: () => void
}

const candidates = [
  {
    id: 'candidate-001',
    name: 'Amara Okafor',
    score: 91,
    requiredCoverage: '4 / 4',
    requiredPercentage: 100,
    preferredCoverage: '2 / 3',
    experience: '5 years',
    education: "Bachelor's degree",
    responsibilitiesScore: 92,
    matchedSkills: ['Python', 'FastAPI', 'SQL', 'REST APIs'],
    gaps: ['AWS'],
    evidence:
      'Built and maintained Python backend services and REST APIs, with experience using FastAPI and PostgreSQL.',
  },
  {
    id: 'candidate-002',
    name: 'Daniel Mensah',
    score: 84,
    requiredCoverage: '3 / 4',
    requiredPercentage: 75,
    preferredCoverage: '2 / 3',
    experience: '4 years',
    education: "Bachelor's degree",
    responsibilitiesScore: 86,
    matchedSkills: ['Python', 'SQL', 'REST APIs'],
    gaps: ['FastAPI', 'AWS'],
    evidence:
      'Developed backend services in Python and worked extensively with SQL databases and REST API integrations.',
  },
  {
    id: 'candidate-003',
    name: 'Chinonso Eze',
    score: 76,
    requiredCoverage: '3 / 4',
    requiredPercentage: 75,
    preferredCoverage: '1 / 3',
    experience: '3 years',
    education: "Bachelor's degree",
    responsibilitiesScore: 78,
    matchedSkills: ['Python', 'SQL', 'Docker'],
    gaps: ['FastAPI', 'REST APIs'],
    evidence:
      'Worked with Python and relational databases, with additional Docker experience across backend projects.',
  },
]

function CandidateComparison({
  onBack,
}: CandidateComparisonProps) {
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<string[]>(
    [],
  )
  const [showComparison, setShowComparison] = useState(false)

  const selectedCandidates = candidates.filter((candidate) =>
    selectedCandidateIds.includes(candidate.id),
  )

  const toggleCandidate = (candidateId: string) => {
    setSelectedCandidateIds((current) => {
      if (current.includes(candidateId)) {
        return current.filter((id) => id !== candidateId)
      }

      if (current.length >= 3) {
        return current
      }

      return [...current, candidateId]
    })

    setShowComparison(false)
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
          <span className="page-eyebrow">Candidate comparison</span>

          <h2>Put the strongest matches side by side.</h2>

          <p>
            Select up to three candidates to compare their matching signals,
            evidence and skill gaps before making a recruiter decision.
          </p>
        </div>

        <div className="comparison-selection-count">
          <strong>{selectedCandidateIds.length}</strong>
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

        <div className="comparison-candidate-list">
          {candidates.map((candidate) => {
            const selected = selectedCandidateIds.includes(candidate.id)

            return (
              <button
                key={candidate.id}
                type="button"
                className={`comparison-candidate-option ${
                  selected ? 'selected' : ''
                }`}
                onClick={() => toggleCandidate(candidate.id)}
              >
                <span className="comparison-checkbox">
                  {selected ? '✓' : ''}
                </span>

                <span className="comparison-option-avatar">
                  {candidate.name
                    .split(' ')
                    .map((name) => name[0])
                    .join('')}
                </span>

                <span className="comparison-option-info">
                  <strong>{candidate.name}</strong>
                  <small>
                    Rank #{candidates.indexOf(candidate) + 1} ·{' '}
                    {candidate.requiredCoverage} required
                  </small>
                </span>

                <span className="comparison-option-score">
                  {candidate.score}%
                </span>
              </button>
            )
          })}
        </div>

        <div className="comparison-selection-actions">
          <span>
            {selectedCandidateIds.length < 2
              ? 'Select at least two candidates'
              : `${selectedCandidateIds.length} candidates ready to compare`}
          </span>

          <button
            type="button"
            className="comparison-compare-button"
            disabled={selectedCandidateIds.length < 2}
            onClick={() => {
              setShowComparison(true)

              window.setTimeout(() => {
                document
                  .querySelector('.comparison-results')
                  ?.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start',
                  })
              }, 0)
            }}
          >
            Compare selected
            <span aria-hidden="true">→</span>
          </button>
        </div>
      </section>

      {showComparison && selectedCandidates.length >= 2 && (
        <>
          <section className="comparison-results">
            <div className="comparison-results-header">
              <div>
                <span>Evidence comparison</span>
                <h3>Candidate differences</h3>
              </div>

              <span>Matching engine results</span>
            </div>

            <div className="comparison-table-wrapper">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Dimension</th>

                    {selectedCandidates.map((candidate) => (
                      <th key={candidate.id}>
                        <div className="comparison-table-candidate">
                          <strong>{candidate.name}</strong>
                          <span>
                            Rank #
                            {candidates.indexOf(candidate) + 1}
                          </span>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  <tr>
                    <td>Overall fit</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <strong className="comparison-score">
                          {candidate.score}%
                        </strong>
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Required skill coverage</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <strong>
                          {candidate.requiredCoverage}
                        </strong>

                        <span className="comparison-metric-detail">
                          {candidate.requiredPercentage}% coverage
                        </span>
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Preferred skill coverage</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <strong>{candidate.preferredCoverage}</strong>
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Relevant experience</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        {candidate.experience}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Education</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        {candidate.education}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Responsibilities alignment</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <strong>
                          {candidate.responsibilitiesScore}%
                        </strong>
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Matched skills</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <div className="comparison-skill-list">
                          {candidate.matchedSkills.map((skill) => (
                            <span
                              key={skill}
                              className="comparison-skill matched"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Skill gaps</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <div className="comparison-skill-list">
                          {candidate.gaps.map((gap) => (
                            <span
                              key={gap}
                              className="comparison-skill gap"
                            >
                              {gap}
                            </span>
                          ))}
                        </div>
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td>Supporting evidence</td>

                    {selectedCandidates.map((candidate) => (
                      <td key={candidate.id}>
                        <p className="comparison-evidence">
                          {candidate.evidence}
                        </p>
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="comparison-ai-panel">
            <div className="comparison-results-header">
              <div>
                <span>Grounded explanation</span>
                <h3>What the evidence suggests</h3>
              </div>

              <span>Groq · Explanation only</span>
            </div>

            <div className="comparison-ai-content">
              <p>
                {selectedCandidates[0].name} demonstrates the strongest
                overall match among the selected candidates, with{' '}
                {selectedCandidates[0].requiredPercentage}% coverage of the
                required skills and strong alignment with the role
                responsibilities. The other selected candidates also
                demonstrate relevant experience, but have gaps in one or more
                required skills.
              </p>

              <div className="comparison-ai-tradeoffs">
                <div>
                  <span>Strongest evidence</span>
                  <strong>
                    Required skill coverage and direct technical evidence
                  </strong>
                </div>

                <div>
                  <span>Key trade-off</span>
                  <strong>
                    Technical skill gaps may require additional validation
                  </strong>
                </div>

                <div>
                  <span>Review consideration</span>
                  <strong>
                    Validate missing skills during the interview process
                  </strong>
                </div>
              </div>
            </div>
          </section>

          <div className="comparison-responsible-note">
            <strong>Recruiter decision required</strong>

            <span>
              TalentMatch compares evidence and explains the matching results.
              It does not make hiring decisions.
            </span>
          </div>
        </>
      )}
    </div>
  )
}

export default CandidateComparison