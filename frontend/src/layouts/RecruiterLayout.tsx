import type { ReactNode } from 'react'

type RecruiterPage = 'setup' | 'dashboard' | 'review' | 'comparison'

interface RecruiterLayoutProps {
  activePage: RecruiterPage
  onNavigate: (page: RecruiterPage) => void
  children: ReactNode
}

type NavItem = {
  id: RecruiterPage
  label: string
  description: string
}

const navItems: NavItem[] = [
  {
    id: 'setup',
    label: 'Screening',
    description: 'Set up a role',
  },
  {
    id: 'dashboard',
    label: 'Candidates',
    description: 'Review matches',
  },
  {
    id: 'comparison',
    label: 'Compare',
    description: 'Compare candidates',
  },
]

function RecruiterLayout({
  activePage,
  onNavigate,
  children,
}: RecruiterLayoutProps) {
  const activeItem = navItems.find((item) => item.id === activePage)

  return (
    <div className="recruiter-app">
      <header className="recruiter-header">
        <button
          type="button"
          className="recruiter-brand"
          onClick={() => {
            onNavigate('setup')
          }}
          aria-label="Go to screening"
        >
          <span className="recruiter-brand-mark">T</span>

          <span className="recruiter-brand-name">
            <strong>TalentMatch</strong>
            <small>AI</small>
          </span>
        </button>

        <div className="recruiter-header-context">
          <span>Recruiter workspace</span>

          <span className="recruiter-status">
            <i />
            Local processing
          </span>
        </div>

        <button
          type="button"
          className="recruiter-exit-button"
          onClick={() => {
            window.location.reload()
          }}
        >
          Exit workspace
        </button>
      </header>

      <div className="recruiter-body">
        <aside className="recruiter-sidebar">
          <div className="recruiter-sidebar-heading">
            <span>Workspace</span>
          </div>

          <nav className="recruiter-nav" aria-label="Recruiter workspace">
            {navItems.map((item) => {
              const isActive = item.id === activePage

              return (
                <button
                  key={item.id}
                  type="button"
                  className={`recruiter-nav-item ${
                    isActive ? 'active' : ''
                  }`}
                  onClick={() => onNavigate(item.id)}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <span className="recruiter-nav-indicator" />

                  <span className="recruiter-nav-copy">
                    <strong>{item.label}</strong>
                    <small>{item.description}</small>
                  </span>
                </button>
              )
            })}
          </nav>

          <div className="recruiter-sidebar-footer">
            <span className="recruiter-sidebar-footer-label">
              Matching engine
            </span>

            <strong>Evidence-based</strong>

            <p>
              Scores and rankings are determined by the matching engine.
            </p>
          </div>
        </aside>

        <main className="recruiter-main">
          <div className="recruiter-page-heading">
            <div>
              <span className="recruiter-page-eyebrow">TalentMatch</span>
              <h1>{activeItem?.label ?? 'Workspace'}</h1>
            </div>

            <span className="recruiter-page-status">
              {activeItem?.description}
            </span>
          </div>

          <div className="recruiter-content">{children}</div>
        </main>
      </div>
    </div>
  )
}

export default RecruiterLayout