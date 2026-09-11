import { useRef, useState } from 'react'

type InputMode = 'paste' | 'upload'

interface ScreeningSetupProps {
    onScreeningComplete: () => void
}

function ScreeningSetup({ onScreeningComplete }: ScreeningSetupProps) {
    const [inputMode, setInputMode] = useState<InputMode>('paste')
    const [jobTitle, setJobTitle] = useState('')
    const [jobDescription, setJobDescription] = useState('')
    const [jobFile, setJobFile] = useState<File | null>(null)
    const [resumeFiles, setResumeFiles] = useState<File[]>([])

    const jobFileInputRef = useRef<HTMLInputElement>(null)
    const resumeFileInputRef = useRef<HTMLInputElement>(null)

    const handleJobFileChange = (
        event: React.ChangeEvent<HTMLInputElement>,
    ) => {
        const file = event.target.files?.[0]

        if (file) {
            setJobFile(file)
        }
    }

    const handleResumeFilesChange = (
        event: React.ChangeEvent<HTMLInputElement>,
    ) => {
        const files = Array.from(event.target.files ?? [])

        if (files.length > 0) {
            setResumeFiles(files)
        }
    }

    const canRunScreening =
        (jobDescription.trim().length > 0 || jobFile !== null) &&
        resumeFiles.length > 0

    return (
        <div className="screening-setup">
            
            <div className="setup-grid">
                {/* Job Description */}
                <section className="panel">
                    <div className="panel-header">
                        <div>
                            <span className="eyebrow">Role definition</span>
                            <h2>Job Description</h2>
                            <p>
                                Provide the role requirements for evaluation.
                            </p>
                        </div>

                        <span className="status-badge">Required</span>
                    </div>
                    <div className="panel-content">
                        <label htmlFor="job-title">Job title</label>

                        <input
                            id="job-title"
                            type="text"
                            placeholder="e.g. Senior Python Developer"
                            value={jobTitle}
                            onChange={(event) => setJobTitle(event.target.value)}
                        />

                        <div className="input-mode">
                            <button
                                type="button"
                                className={`mode-button ${inputMode === 'paste' ? 'active' : ''
                                    }`}
                                onClick={() => setInputMode('paste')}
                            >
                                Paste
                            </button>

                            <button
                                type="button"
                                className={`mode-button ${inputMode === 'upload' ? 'active' : ''
                                    }`}
                                onClick={() => setInputMode('upload')}
                            >
                                Upload
                            </button>
                        </div>

                        {inputMode === 'paste' ? (
                            <>
                                <label htmlFor="job-description">
                                    Job description
                                </label>

                                <textarea
                                    id="job-description"
                                    rows={12}
                                    placeholder="Paste the full job description here..."
                                    value={jobDescription}
                                    onChange={(event) =>
                                        setJobDescription(event.target.value)
                                    }
                                />
                            </>
                        ) : (
                            <div className="upload-zone">
                                <input
                                    ref={jobFileInputRef}
                                    type="file"
                                    accept=".pdf,.docx,.txt"
                                    hidden
                                    onChange={handleJobFileChange}
                                />

                                <div className="upload-icon">JD</div>

                                <h3>
                                    {jobFile ? jobFile.name : 'Upload a job description'}
                                </h3>

                                <p>
                                    PDF, DOCX, or TXT files are supported.
                                </p>

                                <button
                                    type="button"
                                    className="secondary-button"
                                    onClick={() => jobFileInputRef.current?.click()}
                                >
                                    {jobFile ? 'Choose another file' : 'Choose file'}
                                </button>
                            </div>
                        )}
                    </div>
                </section>

                {/* Candidate Pool */}
                <section className="panel">
                    <div className="panel-header">
                        <div>
                            <span className="eyebrow">Candidate intake</span>
                            <h2>Candidate Pool</h2>
                            <p>
                                Upload the resumes you want TalentMatch to screen.
                            </p>
                        </div>

                        <span className="status-badge">Required</span>
                    </div>

                    <div className="panel-content">
                        <input
                            ref={resumeFileInputRef}
                            type="file"
                            accept=".pdf,.docx,.txt"
                            multiple
                            hidden
                            onChange={handleResumeFilesChange}
                        />

                        <div className="upload-zone candidate-upload">
                            <div className="upload-icon">CV</div>

                            <h3>Upload candidate resumes</h3>

                            <p>
                                Add multiple PDF, DOCX, or TXT resumes for batch
                                screening.
                            </p>

                            <button
                                type="button"
                                className="secondary-button"
                                onClick={() => resumeFileInputRef.current?.click()}
                            >
                                Upload resumes
                            </button>
                        </div>

                        {resumeFiles.length > 0 && (
                            <div className="file-summary">
                                <div className="file-summary-main">
                                    <div className="file-summary-count">
                                        <strong>{resumeFiles.length}</strong>
                                    </div>

                                    <div>
                                        <strong>
                                            {resumeFiles.length === 1
                                                ? 'Resume ready'
                                                : 'Resumes ready'}
                                        </strong>

                                        <span>
                                            Ready for batch screening
                                        </span>
                                    </div>
                                </div>

                                <span className="status-badge">Ready</span>
                            </div>
                        )}
                    </div>
                </section>
            </div>

            {/* Screening Action */}
            <section className="screening-action">
                <div>
                    <span className="eyebrow">Ready to screen?</span>
                    <h2>Run the candidate screening</h2>
                    <p>
                        TalentMatch will process the job description and
                        candidate pool, then generate ranked results.
                    </p>
                </div>

                <button
                    type="button"
                    className="primary-button"
                    disabled={!canRunScreening}
                    onClick={onScreeningComplete}
                >
                    Run Candidate Screening
                </button>
            </section>
        </div>
    )
}

export default ScreeningSetup