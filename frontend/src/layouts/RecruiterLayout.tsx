import type { ReactNode } from 'react'

interface RecruiterLayoutProps {
  children: ReactNode
}

function RecruiterLayout({ children }: RecruiterLayoutProps) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">T</div>
          <div>
            <span className="brand-name">TalentMatch AI</span>
            <span className="brand-subtitle">Recruiter screening workspace</span>
          </div>
        </div>

        <div className="topbar-status">
          <span className="status-dot" />
          Local processing
        </div>
      </header>

      <main className="workspace">
        <section className="workspace-header">
          <div>
            <p className="eyebrow">Recruiter workspace</p>
            <h1>Screen candidates with evidence, not guesswork.</h1>
            <p className="workspace-description">
              Define the role, process your candidate pool, and review
              explainable matches from one workspace.
            </p>
          </div>

          <button type="button" className="primary-button">
            New screening
          </button>
        </section>

        <nav className="workspace-nav" aria-label="Screening workflow">
          <button type="button" className="nav-item active">
            <span className="nav-number">01</span>
            Screening Setup
          </button>

          <button type="button" className="nav-item">
            <span className="nav-number">02</span>
            Candidate Dashboard
          </button>

          <button type="button" className="nav-item">
            <span className="nav-number">03</span>
            Candidate Review
          </button>
        </nav>

        {children}
      </main>
    </div>
  )
}

export default RecruiterLayout