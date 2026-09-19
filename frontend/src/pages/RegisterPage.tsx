import { useState } from 'react'
import type { SubmitEvent } from 'react'
import { register } from '../services/api'

interface RegisterPageProps {
  onRegisterSuccess: () => void
  onLogin: () => void
  onBack: () => void
}

function RegisterPage({
  onRegisterSuccess,
  onLogin,
  onBack,
}: RegisterPageProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] =
    useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: SubmitEvent) => {
    event.preventDefault()

    setError(null)

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)

    try {
      await register(name, email, password)
      onRegisterSuccess()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create your account.',
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
            Create your account.
          </h1>

          <p
            style={{
              marginBottom: '32px',
            }}
          >
            Create an account to start screening
            candidates with TalentMatch.
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
                <span>Name</span>

                <input
                  type="text"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                  placeholder="Your name"
                  autoComplete="name"
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
                  placeholder="Create a password"
                  autoComplete="new-password"
                  minLength={8}
                  maxLength={128}
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

                <small
                  style={{
                    color: '#6B6B63',
                    fontSize: '13px',
                  }}
                >
                  Password must be at least 8 characters.
                </small>
              </label>

              <label
                style={{
                  display: 'grid',
                  gap: '8px',
                }}
              >
                <span>Confirm password</span>

                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(event.target.value)
                  }
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                  minLength={8}
                  maxLength={128}
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
                  ? 'Creating account...'
                  : 'Create account'}

                <span aria-hidden="true">→</span>
              </button>
            </div>
          </form>

          <div
            style={{
              marginTop: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span>Already have an account?</span>

            <button
              type="button"
              onClick={onLogin}
              style={{
                border: 'none',
                background: 'transparent',
                padding: 0,
                cursor: 'pointer',
                font: 'inherit',
                fontWeight: 600,
                textDecoration: 'underline',
              }}
            >
              Log in
            </button>
          </div>

          <button
            type="button"
            onClick={onBack}
            style={{
              marginTop: '16px',
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

export default RegisterPage
