import { useMemo, useState } from 'react'

const mockRequirements = {
    requiredSkills: ['Python', 'FastAPI', 'SQL', 'REST APIs'],
    preferredSkills: ['Docker', 'AWS', 'Git'],
    experience: '3+ years',
    education: "Bachelor's degree in Computer Science or related field",
    responsibilities: [
        'Build and maintain backend services',
        'Design and integrate REST APIs',
        'Work with relational databases',
        'Collaborate with frontend and engineering teams',
    ],
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

interface CandidateDashboardProps {
    onCandidateSelect: (candidateId: string) => void
}

function CandidateDashboard({
    onCandidateSelect,
}: CandidateDashboardProps) {
    const [searchTerm, setSearchTerm] = useState('')
    const [minScore, setMinScore] = useState('all')
    const [skillCoverage, setSkillCoverage] = useState('all')

    const filteredCandidates = useMemo(() => {
        return mockCandidates.filter((candidate) => {
            const matchesSearch =
                candidate.name
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase()) ||
                candidate.id
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase())

            const matchesScore =
                minScore === 'all' ||
                candidate.score >= Number(minScore)

            const [matched, total] = candidate.requiredSkills
                .split('/')
                .map((value) => Number(value.trim()))

            const hasFullCoverage = matched === total

            const matchesCoverage =
                skillCoverage === 'all' ||
                (skillCoverage === 'full' && hasFullCoverage) ||
                (skillCoverage === 'partial' && !hasFullCoverage)

            return matchesSearch && matchesScore && matchesCoverage
        })
    }, [searchTerm, minScore, skillCoverage])
    return (
        <div className="candidate-dashboard">
            {/* Extracted Requirements */}
            <section className="panel">
                <div className="panel-header">
                    <div>
                        <span className="eyebrow">Job Requirements</span>
                        <h2>Extracted Requirements</h2>
                        <p>
                            Requirements extracted from the submitted job description.
                        </p>
                    </div>

                    <span className="status-badge">Ready</span>
                </div>

                <div className="requirements-grid">
                    <div className="requirement-group">
                        <span className="requirement-label">Required skills</span>

                        <div className="skill-list">
                            {mockRequirements.requiredSkills.map((skill) => (
                                <span
                                    key={skill}
                                    className="skill-tag required"
                                >
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div className="requirement-group">
                        <span className="requirement-label">Preferred skills</span>

                        <div className="skill-list">
                            {mockRequirements.preferredSkills.map((skill) => (
                                <span key={skill} className="skill-tag">
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div className="requirement-group">
                        <span className="requirement-label">Experience</span>
                        <strong>{mockRequirements.experience}</strong>
                    </div>

                    <div className="requirement-group">
                        <span className="requirement-label">Education</span>
                        <strong>{mockRequirements.education}</strong>
                    </div>

                    <div className="requirement-group full-width">
                        <span className="requirement-label">Responsibilities</span>

                        <ul className="responsibility-list">
                            {mockRequirements.responsibilities.map(
                                (responsibility) => (
                                    <li key={responsibility}>
                                        {responsibility}
                                    </li>
                                ),
                            )}
                        </ul>
                    </div>
                </div>
            </section>

            {/* Candidate Rankings */}
            <section className="panel candidate-results-panel">
                <div className="panel-header">
                    <div>
                        <span className="eyebrow">Candidate Results</span>
                        <h2>Candidate Rankings</h2>
                        <p>
                            Ranked by TalentMatch's deterministic matching
                            and scoring engine.
                        </p>
                    </div>

                    <span className="status-badge">
                        {filteredCandidates.length} of {mockCandidates.length} candidates
                    </span>
                </div>

                <div className="candidate-toolbar">
                    <div className="candidate-search">
                        <input
                            type="text"
                            placeholder="Search candidates..."
                            aria-label="Search candidates"
                            value={searchTerm}
                            onChange={(event) => setSearchTerm(event.target.value)}
                        />
                    </div>

                    <select
                        className="candidate-filter"
                        value={minScore}
                        onChange={(event) => setMinScore(event.target.value)}
                        aria-label="Filter by minimum score"
                    >
                        <option value="all">All scores</option>
                        <option value="80">80% and above</option>
                        <option value="70">70% and above</option>
                        <option value="60">60% and above</option>
                        <option value="50">50% and above</option>
                    </select>

                    <select
                        className="candidate-filter"
                        value={skillCoverage}
                        onChange={(event) => setSkillCoverage(event.target.value)}
                        aria-label="Filter by required skill coverage"
                    >
                        <option value="all">All skill coverage</option>
                        <option value="full">Full coverage</option>
                        <option value="partial">Partial coverage</option>
                    </select>
                </div>

                <div className="candidate-table-wrapper">
                    <table className="candidate-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Candidate</th>
                                <th>Fit</th>
                                <th>Required skills</th>
                                <th>Matched skills</th>
                                <th>Missing skills</th>
                                <th>Status</th>
                            </tr>
                        </thead>

                        <tbody>
                            {filteredCandidates.map((candidate) => (
                                <tr
                                    key={candidate.id}
                                    onClick={() =>
                                        onCandidateSelect(candidate.id)
                                    }
                                    className="candidate-row"
                                >
                                    <td>
                                        <span className="rank-number">
                                            #{candidate.rank}
                                        </span>
                                    </td>

                                    <td>
                                        <div className="candidate-name-cell">
                                            <strong>{candidate.name}</strong>
                                            <span>{candidate.id}</span>
                                        </div>
                                    </td>

                                    <td>
                                        <div className="fit-score-cell">
                                            <span className="fit-score">
                                                {candidate.score}%
                                            </span>

                                            <div className="fit-score-track">
                                                <div
                                                    className="fit-score-fill"
                                                    style={{
                                                        width: `${candidate.score}%`,
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </td>

                                    <td>
                                        <span className="coverage-value">
                                            {candidate.requiredSkills}
                                        </span>
                                    </td>

                                    <td>
                                        <div className="table-skill-list">
                                            {candidate.matchedSkills.map(
                                                (skill) => (
                                                    <span
                                                        key={skill}
                                                        className="skill-tag"
                                                    >
                                                        {skill}
                                                    </span>
                                                ),
                                            )}
                                        </div>
                                    </td>

                                    <td>
                                        <div className="table-skill-list">
                                            {candidate.missingSkills.map(
                                                (skill) => (
                                                    <span
                                                        key={skill}
                                                        className="skill-tag missing"
                                                    >
                                                        {skill}
                                                    </span>
                                                ),
                                            )}
                                        </div>
                                    </td>

                                    <td>
                                        <span className="status-badge">
                                            {candidate.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    )
}

export default CandidateDashboard