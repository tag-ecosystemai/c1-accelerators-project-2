import { useState } from 'react'
import type { SubmitEvent } from 'react'
import { login } from '../services/api'

interface LoginPageProps {
  onLoginSuccess: () => void
  onBack: () => void
}

function LoginPage({
  onLoginSuccess,
  onBack,
}: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: SubmitEvent) => {
    event.preventDefault()

    setLoading(true)
    setError(null)

    try {
      await login(email, password)
      onLoginSuccess()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to log in.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="landing-page">
      <header className="landing-header">
        <button
          type="button"
          className="landing-logo"
          onClick={onBack}
          style={{
            border: 'none',
            background: 'none',
            padding: 0,
            cursor: 'pointer',
          }}
        >
          <span className="landing-logo-mark">T</span>

          <span>
            <strong>TalentMatch</strong>
            <small>AI</small>
          </span>
        </button>
      </header>

      <section
        style={{
          minHeight: '70vh',
          display: 'grid',
          placeItems: 'center',
          padding: '48px 24px',
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '440px',
          }}
        >
          <span className="landing-eyebrow">
            Recruiter workspace
          </span>

          <h1
            style={{
              marginTop: '12px',
              marginBottom: '12px',
            }}
          >
            Welcome back.
          </h1>

          <p
            style={{
              marginBottom: '32px',
            }}
          >
            Log in to continue screening candidates
            with TalentMatch.
          </p>

          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: 'grid',
                gap: '20px',
              }}
            >
              <label
                style={{
                  display: 'grid',
                  gap: '8px',
                }}
              >
                <span>Email</span>

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  placeholder="recruiter@example.com"
                  autoComplete="email"
                  required
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    border: '1px solid #E6E1DA',
                    borderRadius: '8px',
                    font: 'inherit',
                    boxSizing: 'border-box',
                  }}
                />
              </label>

              <label
                style={{
                  display: 'grid',
                  gap: '8px',
                }}
              >
                <span>Password</span>

                <input
                  type="password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    border: '1px solid #E6E1DA',
                    borderRadius: '8px',
                    font: 'inherit',
                    boxSizing: 'border-box',
                  }}
                />
              </label>

              {error && (
                <div
                  role="alert"
                  style={{
                    padding: '12px 14px',
                    border: '1px solid #E6E1DA',
                    borderRadius: '8px',
                    background: '#FBE4D6',
                  }}
                >
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="landing-primary-button"
                disabled={loading}
              >
                {loading
                  ? 'Logging in...'
                  : 'Log in'}

                <span aria-hidden="true">→</span>
              </button>
            </div>
          </form>

          <button
            type="button"
            onClick={onBack}
            style={{
              marginTop: '20px',
              border: 'none',
              background: 'transparent',
              padding: 0,
              cursor: 'pointer',
              font: 'inherit',
            }}
          >
            ← Back to landing page
          </button>
        </div>
      </section>
    </main>
  )
}

export default LoginPage
