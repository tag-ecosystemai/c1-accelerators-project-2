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
        name: 'Daniel Okoro',
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
    const [selectedCandidateIds, setSelectedCandidateIds] =
        useState<string[]>([])
    const [showComparison, setShowComparison] = useState(false)

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
    }

    return (
        <div className="candidate-comparison">
            <section className="comparison-header">
                <div>
                    <span className="eyebrow">Candidate Comparison</span>

                    <h1>Compare candidates</h1>

                    <p>
                        Select up to three candidates to compare their
                        matching results side by side.
                    </p>
                </div>

                <button
                    type="button"
                    className="secondary-button"
                    onClick={onBack}
                >
                    Back to Candidates
                </button>
            </section>

            <section className="panel">
                <div className="panel-header">
                    <div>
                        <span className="eyebrow">Selection</span>
                        <h2>Select candidates</h2>
                        <p>
                            Choose up to three candidates for comparison.
                        </p>
                    </div>

                    <div className="comparison-selection-actions">
                        <span className="status-badge">
                            {selectedCandidateIds.length}/3 selected
                        </span>

                        <button
                            type="button"
                            className="primary-button"
                            disabled={selectedCandidateIds.length < 2}
                            onClick={() => {
                                setShowComparison(true)

                                setTimeout(() => {
                                    document
                                        .querySelector('.comparison-results')
                                        ?.scrollIntoView({ behavior: 'smooth' })
                                }, 0)
                            }}
                        >
                            Compare selected
                        </button>
                    </div>
                </div>

                <div className="comparison-candidate-list">
                    {candidates.map((candidate) => {
                        const selected = selectedCandidateIds.includes(
                            candidate.id,
                        )

                        return (
                            <button
                                type="button"
                                className={`comparison-candidate ${selected ? 'selected' : ''
                                    }`}
                                key={candidate.id}
                                onClick={() => toggleCandidate(candidate.id)}
                            >
                                <span className="comparison-checkbox">
                                    {selected ? '✓' : ''}
                                </span>

                                <span className="comparison-candidate-info">
                                    <strong>{candidate.name}</strong>
                                    <span>{candidate.id}</span>
                                </span>

                                <span className="comparison-candidate-score">
                                    {candidate.score}%
                                </span>
                            </button>
                        )
                    })}
                </div>
            </section>

            {showComparison && selectedCandidateIds.length >= 2 && (
                <section className="panel comparison-results">
                    <div className="panel-header">
                        <div>
                            <span className="eyebrow">Comparison</span>
                            <h2>Candidate results</h2>
                            <p>
                                Deterministic matching results displayed side by side.
                            </p>
                        </div>
                    </div>

                    <div className="comparison-table-wrapper">
                        <table className="comparison-table">
                            <thead>
                                <tr>
                                    <th>Metric</th>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <th key={candidateId}>
                                                <div className="comparison-table-candidate">
                                                    <strong>{candidate?.name}</strong>
                                                    <span>{candidate?.id}</span>
                                                </div>
                                            </th>
                                        )
                                    })}
                                </tr>
                            </thead>

                            <tbody>
                                <tr>
                                    <td>Overall fit</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                <strong className="comparison-score">
                                                    {candidate?.score}%
                                                </strong>
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Required skills</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                <strong>
                                                    {candidate?.requiredCoverage}
                                                </strong>
                                                <span className="comparison-metric-detail">
                                                    {candidate?.requiredPercentage}% coverage
                                                </span>
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Preferred skills</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                {candidate?.preferredCoverage}
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Relevant experience</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                {candidate?.experience}
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Education</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                {candidate?.education}
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Responsibilities alignment</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                {candidate?.responsibilitiesScore}%
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Matched skills</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                <div className="comparison-skill-list">
                                                    {candidate?.matchedSkills.map((skill) => (
                                                        <span
                                                            className="comparison-skill matched"
                                                            key={skill}
                                                        >
                                                            {skill}
                                                        </span>
                                                    ))}
                                                </div>
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Major gaps</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                <div className="comparison-skill-list">
                                                    {candidate?.gaps.map((skill) => (
                                                        <span
                                                            className="comparison-skill gap"
                                                            key={skill}
                                                        >
                                                            {skill}
                                                        </span>
                                                    ))}
                                                </div>
                                            </td>
                                        )
                                    })}
                                </tr>

                                <tr>
                                    <td>Relevant evidence</td>

                                    {selectedCandidateIds.map((candidateId) => {
                                        const candidate = candidates.find(
                                            (item) => item.id === candidateId,
                                        )

                                        return (
                                            <td key={candidateId}>
                                                <p className="comparison-evidence">
                                                    {candidate?.evidence}
                                                </p>
                                            </td>
                                        )
                                    })}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>
            )}

            {selectedCandidateIds.length < 2 && (
                <section className="panel comparison-empty-state">
                    <span className="eyebrow">Comparison</span>

                    <h2>
                        {selectedCandidateIds.length === 0
                            ? 'Select candidates to begin'
                            : 'Select at least one more candidate'}
                    </h2>

                    <p>
                        Select two or three candidates above to view their
                        matching results side by side.
                    </p>
                </section>
            )}
            {showComparison && selectedCandidateIds.length >= 2 && (
                <section className="panel comparison-ai-panel">
                    <div className="panel-header">
                        <div>
                            <span className="eyebrow">AI Explanation</span>
                            <h2>Comparison Summary</h2>
                            <p>
                                A grounded explanation of the selected candidates'
                                matching results and supporting evidence.
                            </p>
                        </div>

                        <span className="status-badge">LLM Explanation</span>
                    </div>

                    <div className="comparison-ai-content">
                        <div className="explanation-notice">
                            <strong>Evidence-based comparison</strong>
                            <span>
                                The LLM explains the matching engine's results. It does not
                                determine candidate scores or rankings.
                            </span>
                        </div>

                        <p>
                            Amara Okafor demonstrates the strongest overall match among
                            the selected candidates, with full coverage of the required
                            skills and strong alignment with the role responsibilities.
                            Daniel Okoro also demonstrates relevant backend experience,
                            but has gaps in FastAPI and AWS. Chinonso Eze shows relevant
                            Python and database experience, although the available
                            evidence indicates weaker alignment with the required
                            FastAPI and REST API skills.
                        </p>

                        <div className="comparison-ai-tradeoffs">
                            <div>
                                <span>Strongest evidence</span>
                                <strong>Required skill coverage</strong>
                            </div>

                            <div>
                                <span>Key trade-off</span>
                                <strong>Technical skill gaps</strong>
                            </div>

                            <div>
                                <span>Review consideration</span>
                                <strong>Validate missing skills during interview</strong>
                            </div>
                        </div>
                    </div>
                </section>
            )}
        </div>
    )
}

export default CandidateComparison