import { useMemo, useState } from 'react'

interface CandidateDashboardProps {
  onCandidateSelect: (candidateId: string) => void
}

const mockRequirements = {
  requiredSkills: ['Python', 'FastAPI', 'SQL', 'REST APIs'],
  preferredSkills: ['Docker', 'AWS', 'Git'],
  experience: '3+ years',
  education: "Bachelor's degree in Computer Science or related field",
}

const mockCandidates = [
  {
    id: 'candidate-001',
    rank: 1,
    name: 'Amara Okafor',
    score: 91,
    requiredSkills: '4 / 4',
    matchedSkills: ['Python', 'FastAPI', 'SQL', 'REST APIs'],
    missingSkills: ['AWS'],
    status: 'Processed',
  },
  {
    id: 'candidate-002',
    rank: 2,
    name: 'Daniel Mensah',
    score: 84,
    requiredSkills: '4 / 4',
    matchedSkills: ['Python', 'SQL', 'REST APIs'],
    missingSkills: ['FastAPI', 'AWS'],
    status: 'Processed',
  },
  {
    id: 'candidate-003',
    rank: 3,
    name: 'Chinonso Eze',
    score: 76,
    requiredSkills: '3 / 4',
    matchedSkills: ['Python', 'SQL', 'Docker'],
    missingSkills: ['FastAPI', 'REST APIs'],
    status: 'Processed',
  },
]

function CandidateDashboard({
  onCandidateSelect,
}: CandidateDashboardProps) {
  const [search, setSearch] = useState('')
  const [minimumScore, setMinimumScore] = useState('')
  const [requiredCoverage, setRequiredCoverage] = useState('')

  const filteredCandidates = useMemo(() => {
    return mockCandidates.filter((candidate) => {
      const matchesSearch =
        candidate.name.toLowerCase().includes(search.toLowerCase()) ||
        candidate.id.toLowerCase().includes(search.toLowerCase())

      const matchesScore =
        !minimumScore || candidate.score >= Number(minimumScore)

      const [matched, total] = candidate.requiredSkills
        .split('/')
        .map((value) => Number(value.trim()))

      const coverage = total > 0 ? (matched / total) * 100 : 0

      const matchesCoverage =
        !requiredCoverage || coverage >= Number(requiredCoverage)

      return matchesSearch && matchesScore && matchesCoverage
    })
  }, [search, minimumScore, requiredCoverage])

  return (
    <div className="dashboard-page">
      <section className="dashboard-intro">
        <div>
          <span className="page-eyebrow">Screening results</span>

          <h2>Review the shortlist.</h2>

          <p>
            Candidates are ranked by the matching engine. Use the evidence and
            score breakdown to decide who deserves a closer review.
          </p>
        </div>

        <div className="dashboard-result-count">
          <strong>{filteredCandidates.length}</strong>
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
          <strong>Senior Python Engineer</strong>
        </div>

        <div className="dashboard-requirement-group">
          <span>Required</span>

          <div>
            {mockRequirements.requiredSkills.map((skill) => (
              <span key={skill} className="dashboard-skill required">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="dashboard-requirement-group">
          <span>Preferred</span>

          <div>
            {mockRequirements.preferredSkills.map((skill) => (
              <span key={skill} className="dashboard-skill preferred">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="dashboard-requirement-meta">
          <span>{mockRequirements.experience}</span>
          <span>{mockRequirements.education}</span>
        </div>
      </section>

      <section className="dashboard-toolbar">
        <div className="dashboard-search">
          <span aria-hidden="true">⌕</span>

          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search candidates..."
            aria-label="Search candidates"
          />
        </div>

        <select
          value={minimumScore}
          onChange={(event) => setMinimumScore(event.target.value)}
          aria-label="Minimum score"
        >
          <option value="">Any score</option>
          <option value="90">90+</option>
          <option value="80">80+</option>
          <option value="70">70+</option>
        </select>

        <select
          value={requiredCoverage}
          onChange={(event) => setRequiredCoverage(event.target.value)}
          aria-label="Required skill coverage"
        >
          <option value="">Any coverage</option>
          <option value="100">100%</option>
          <option value="75">75%+</option>
          <option value="50">50%+</option>
        </select>
      </section>

      <section className="dashboard-candidates">
        <div className="dashboard-table-header">
          <div>
            <span className="dashboard-table-eyebrow">Candidate ranking</span>
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

          {filteredCandidates.map((candidate) => (
            <button
              key={candidate.id}
              type="button"
              className="dashboard-candidate-row"
              onClick={() => onCandidateSelect(candidate.id)}
            >
              <span className="dashboard-rank">
                {String(candidate.rank).padStart(2, '0')}
              </span>

              <span className="dashboard-candidate">
                <span className="dashboard-avatar">
                  {candidate.name
                    .split(' ')
                    .map((name) => name[0])
                    .join('')}
                </span>

                <span>
                  <strong>{candidate.name}</strong>
                  <small>{candidate.id}</small>
                </span>
              </span>

              <span className="dashboard-fit">
                <strong>{candidate.score}%</strong>

                <span>
                  {candidate.score >= 85
                    ? 'Strong match'
                    : candidate.score >= 75
                      ? 'Good match'
                      : 'Review'}
                </span>
              </span>

              <span className="dashboard-coverage">
                <strong>{candidate.requiredSkills}</strong>

                <span>required</span>
              </span>

              <span className="dashboard-gaps">
                {candidate.missingSkills.length === 0 ? (
                  <span className="dashboard-no-gap">None</span>
                ) : (
                  candidate.missingSkills.map((skill) => (
                    <span key={skill}>{skill}</span>
                  ))
                )}
              </span>

              <span className="dashboard-status">
                <i />
                {candidate.status}
              </span>

              <span className="dashboard-arrow" aria-hidden="true">
                →
              </span>
            </button>
          ))}

          {filteredCandidates.length === 0 && (
            <div className="dashboard-empty">
              <strong>No candidates match these filters.</strong>
              <span>Try widening your search criteria.</span>
            </div>
          )}
        </div>
      </section>

      <div className="dashboard-footnote">
        <span>Human review required</span>

        <p>
          TalentMatch provides matching evidence and rankings. Final hiring
          decisions remain with the recruiter.
        </p>
      </div>
    </div>
  )
}

export default CandidateDashboard