import { useState } from 'react'
import {
  createJob,
  uploadJob,
  uploadResumes,
  type JobCreatedResponse,
} from '../services/api'

interface ScreeningSetupProps {
  onScreeningComplete: (job: JobCreatedResponse) => void
}

function ScreeningSetup({
  onScreeningComplete,
}: ScreeningSetupProps) {
  const [jobDescription, setJobDescription] = useState('')
  const [jobFile, setJobFile] = useState<File | null>(null)
  const [resumeFiles, setResumeFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleJobFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0] ?? null

    setJobFile(file)

    if (file) {
      setJobDescription('')
    }
  }

  const handleResumeUpload = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const files = Array.from(event.target.files ?? [])

    setResumeFiles(files)
  }

  const handleScreening = async () => {
    setError(null)

    if (!jobDescription.trim() && !jobFile) {
      setError(
        'Provide a job description or upload a job description file.',
      )
      return
    }

    if (resumeFiles.length === 0) {
      setError('Upload at least one candidate resume.')
      return
    }

    setLoading(true)

    try {
      let job: JobCreatedResponse

      if (jobFile) {
        job = await uploadJob(jobFile)
      } else {
        job = await createJob(jobDescription)
      }

      await uploadResumes(job.job.id, resumeFiles)

      onScreeningComplete(job)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to start candidate screening.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screening-page">
      <div className="screening-intro">
        <span className="page-eyebrow">
          Candidate screening
        </span>

        <h2>
          Define the role. Let the evidence guide the shortlist.
        </h2>

        <p>
          Start with the job description, add your candidate
          resumes, and TalentMatch will evaluate each candidate
          against the requirements.
        </p>
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
            Paste the role description or upload the original
            document. We’ll use it to identify the requirements
            against which candidates are evaluated.
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
            onChange={(event) => {
              setJobDescription(event.target.value)

              if (event.target.value.trim()) {
                setJobFile(null)
              }
            }}
            placeholder="Paste the job description here..."
            rows={13}
            disabled={loading}
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
              onChange={handleJobFileUpload}
              disabled={loading}
            />

            <span className="screening-file-hint">
              {jobFile
                ? jobFile.name
                : 'PDF, DOCX or TXT'}
            </span>
          </div>
        </section>

        <section className="screening-panel screening-candidate-panel">
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
            Add the resumes you want to evaluate. TalentMatch
            processes the batch and keeps each candidate tied
            to their source evidence.
          </p>

          <div className="screening-candidate-upload-area">
            <div className="screening-candidate-upload-copy">
              <strong>
                Upload candidate resumes
              </strong>

              <span>
                Select one or multiple PDF, DOCX, or TXT files.
              </span>
            </div>

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
                disabled={loading}
              />

              <span className="screening-file-hint">
                {resumeFiles.length > 0
                  ? `${resumeFiles.length} resume${
                      resumeFiles.length === 1
                        ? ''
                        : 's'
                    } selected`
                  : 'PDF, DOCX or TXT · Multiple files supported'}
              </span>
            </div>
          </div>
        </section>
      </div>

      {error && (
        <div
          className="screening-error"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="screening-action-bar">
        <button
          type="button"
          className="screening-run-button"
          onClick={handleScreening}
          disabled={loading}
        >
          {loading
            ? 'Processing resumes...'
            : 'Run candidate screening'}

          <span aria-hidden="true">→</span>
        </button>
      </div>
    </div>
  )
}

export default ScreeningSetup