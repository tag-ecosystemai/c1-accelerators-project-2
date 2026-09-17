import { useEffect, useState } from 'react'

import {
  getJobHistory,
  type JobDescriptionResponse,
} from '../services/api'

interface HistoryProps {
  onOpenScreening: (jobId: number) => void
}

function History({
  onOpenScreening,
}: HistoryProps) {
  const [jobs, setJobs] = useState<JobDescriptionResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadHistory = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await getJobHistory()

        if (!cancelled) {
          setJobs(response.jobs)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load screening history.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadHistory()

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section
      style={{
        maxWidth: '960px',
        margin: '0 auto',
      }}
    >
      <div
        style={{
          marginBottom: '24px',
        }}
      >
        <p
          style={{
            margin: '0 0 6px',
            fontSize: '12px',
            fontWeight: 700,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            opacity: 0.65,
          }}
        >
          Screening history
        </p>

        <h2
          style={{
            margin: 0,
          }}
        >
          Previous screenings
        </h2>

        <p
          style={{
            margin: '8px 0 0',
            opacity: 0.7,
          }}
        >
          Reopen a previous screening without changing its stored results.
        </p>
      </div>

      {loading && (
        <div>
          Loading your screening history...
        </div>
      )}

      {!loading && error && (
        <div
          role="alert"
          style={{
            padding: '16px',
            border: '1px solid #e6e1da',
            borderRadius: '12px',
          }}
        >
          <strong>Unable to load history</strong>

          <p
            style={{
              marginBottom: 0,
            }}
          >
            {error}
          </p>
        </div>
      )}

      {!loading && !error && jobs.length === 0 && (
        <div
          style={{
            padding: '32px',
            border: '1px solid #e6e1da',
            borderRadius: '12px',
            background: '#ffffff',
          }}
        >
          <strong>No previous screenings yet.</strong>

          <p
            style={{
              marginBottom: 0,
              opacity: 0.7,
            }}
          >
            Your screenings will appear here after you create them while
            logged in.
          </p>
        </div>
      )}

      {!loading && !error && jobs.length > 0 && (
        <div
          style={{
            display: 'grid',
            gap: '12px',
          }}
        >
          {jobs.map((job) => (
            <article
              key={job.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '20px',
                padding: '20px',
                border: '1px solid #e6e1da',
                borderRadius: '12px',
                background: '#ffffff',
              }}
            >
              <div
                style={{
                  minWidth: 0,
                }}
              >
                <strong
                  style={{
                    display: 'block',
                    marginBottom: '6px',
                  }}
                >
                  Screening #{job.id}
                </strong>

                <p
                  style={{
                    margin: 0,
                    overflow: 'hidden',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    opacity: 0.75,
                  }}
                >
                  {job.text}
                </p>

                <small
                  style={{
                    display: 'block',
                    marginTop: '8px',
                    opacity: 0.55,
                  }}
                >
                  {new Date(job.created_at).toLocaleString()}
                </small>
              </div>

              <button
                type="button"
                onClick={() => onOpenScreening(job.id)}
              >
                Open screening
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default History