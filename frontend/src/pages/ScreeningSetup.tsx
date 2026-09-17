import { useState } from 'react'

interface ScreeningSetupProps {
    onScreeningComplete: () => void
}

function ScreeningSetup({ onScreeningComplete }: ScreeningSetupProps) {
    const [jobDescription, setJobDescription] = useState('')
    const [resumeCount, setResumeCount] = useState(0)

    const handleResumeUpload = (
        event: React.ChangeEvent<HTMLInputElement>,
    ) => {
        const files = event.target.files

        if (files) {
            setResumeCount(files.length)
        }
    }

    return (
        <div className="screening-page">
            <div className="screening-intro">
                <div>
                    <span className="page-eyebrow">Candidate screening</span>

                    <h2>Define the role. Let the evidence guide the shortlist.</h2>

                    <p>
                        Start with the job description, add your candidate resumes, and
                        TalentMatch will evaluate each candidate against the requirements.
                    </p>
                </div>

                <div className="screening-principle">
                    <span>Matching principle</span>

                    <strong>
                        The engine scores.
                        <br />
                        The evidence explains.
                    </strong>
                </div>
            </div>

            <div className="screening-grid">
                <section className="screening-panel">
                    <div className="screening-panel-header">
                        <div className="screening-step">01</div>

                        <div>
                            <span className="screening-panel-eyebrow">
                                Role definition
                            </span>

                            <h3>Job description</h3>
                        </div>
                    </div>

                    <p className="screening-panel-description">
                        Paste the role description or upload the original document. We’ll
                        use it to identify the requirements against which candidates are
                        evaluated.
                    </p>

                    <label
                        className="screening-field-label"
                        htmlFor="job-description"
                    >
                        Job description
                    </label>

                    <textarea
                        id="job-description"
                        className="screening-textarea"
                        value={jobDescription}
                        onChange={(event) => setJobDescription(event.target.value)}
                        placeholder="Paste the job description here..."
                        rows={13}
                    />

                    <div className="screening-upload-row">
                        <label
                            htmlFor="job-file"
                            className="screening-upload-button"
                        >
                            Choose file
                        </label>

                        <input
                            id="job-file"
                            type="file"
                            accept=".pdf,.docx,.txt"
                        />

                        <span className="screening-file-hint">
                            PDF, DOCX or TXT
                        </span>
                    </div>
                </section>

                <section className="screening-panel">
                    <div className="screening-panel-header">
                        <div className="screening-step peach">02</div>

                        <div>
                            <span className="screening-panel-eyebrow">
                                Candidate pool
                            </span>

                            <h3>Resume batch</h3>
                        </div>
                    </div>

                    <p className="screening-panel-description">
                        Add the resumes you want to evaluate. TalentMatch processes the
                        batch and keeps each candidate tied to their source evidence.
                    </p>

                    <div className="screening-upload-row screening-candidate-upload">
                        <label
                            htmlFor="candidate-files"
                            className="screening-upload-button"
                        >
                            Choose files
                        </label>

                        <input
                            id="candidate-files"
                            type="file"
                            accept=".pdf,.docx,.txt"
                            multiple
                            onChange={handleResumeUpload}
                        />

                        <span className="screening-file-hint">
                            {resumeCount > 0
                                ? `${resumeCount} resume${resumeCount === 1 ? '' : 's'} selected`
                                : 'PDF, DOCX or TXT · Multiple files supported'}
                        </span>
                    </div>
                </section>
            </div>

            <div className="screening-action-bar">
                <div>
                    <span>Ready to screen?</span>

                    <p>
                        Candidate ranking will be determined by the matching engine.
                    </p>
                </div>

                <button
                    type="button"
                    className="screening-run-button"
                    onClick={onScreeningComplete}
                >
                    Run candidate screening
                    <span aria-hidden="true">→</span>
                </button>
            </div>
        </div>
    )
}

export default ScreeningSetup

