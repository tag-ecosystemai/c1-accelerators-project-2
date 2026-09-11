import type { ReactNode } from 'react'

type Page = 'setup' | 'dashboard' | 'review' | 'comparison'

type IconName =
  | 'screening'
  | 'candidates'
  | 'compare'
  | 'settings'
  | 'help'
  | 'bell'

interface RecruiterLayoutProps {
  children: ReactNode
  activePage: Page
  onNavigate: (page: Page) => void
}

interface IconProps {
  name: IconName
  size?: number
}

function Icon({ name, size = 18 }: IconProps) {
  const commonProps = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true,
  }

  switch (name) {
    case 'screening':
      return (
        <svg {...commonProps}>
          <path d="M4 5h16" />
          <path d="M4 9h16" />
          <path d="M4 13h10" />
          <path d="M4 17h7" />
          <path d="M17 15v5" />
          <path d="M14.5 17.5h5" />
        </svg>
      )

    case 'candidates':
      return (
        <svg {...commonProps}>
          <circle cx="9" cy="8" r="3" />
          <path d="M3.5 19c.7-3 2.5-4.5 5.5-4.5s4.8 1.5 5.5 4.5" />
          <path d="M16 11a3 3 0 1 0 0-6" />
          <path d="M16 14.5c2.5.1 4 1.5 4.5 4.5" />
        </svg>
      )

    case 'compare':
      return (
        <svg {...commonProps}>
          <path d="M7 5v14" />
          <path d="m4 8 3-3 3 3" />
          <path d="M17 19V5" />
          <path d="m14 16 3 3 3-3" />
        </svg>
      )

    case 'settings':
      return (
        <svg {...commonProps}>
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-2.6V20a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.6-1H6v-2.6h.4A1.7 1.7 0 0 0 8 10a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.2h2.6V5a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2V14h-.2a1.7 1.7 0 0 0-1.6 1Z" />
        </svg>
      )

    case 'help':
      return (
        <svg {...commonProps}>
          <circle cx="12" cy="12" r="9" />
          <path d="M9.8 9a2.3 2.3 0 1 1 3.8 1.7c-1 .8-1.6 1.2-1.6 2.5" />
          <path d="M12 16.8h.01" />
        </svg>
      )

    case 'bell':
      return (
        <svg {...commonProps}>
          <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
          <path d="M10 21h4" />
        </svg>
      )
  }
}

function RecruiterLayout({
  children,
  activePage,
  onNavigate,
}: RecruiterLayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">T</div>

          <div className="sidebar-brand-copy">
            <span className="brand-name">TalentMatch AI</span>
            <span className="brand-subtitle">Recruiter workspace</span>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          <p className="sidebar-section-label">Workspace</p>

          <button
            type="button"
            className={`sidebar-nav-item ${
              activePage === 'setup' ? 'active' : ''
            }`}
            onClick={() => onNavigate('setup')}
          >
            <span className="sidebar-nav-icon">
              <Icon name="screening" />
            </span>
            <span>Screening</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${
              activePage === 'dashboard' ? 'active' : ''
            }`}
            onClick={() => onNavigate('dashboard')}
          >
            <span className="sidebar-nav-icon">
              <Icon name="candidates" />
            </span>
            <span>Candidates</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${
              activePage === 'comparison' ? 'active' : ''
            }`}
            onClick={() => onNavigate('comparison')}
          >
            <span className="sidebar-nav-icon">
              <Icon name="compare" />
            </span>
            <span>Compare</span>
          </button>

          <div className="sidebar-divider" />

          <p className="sidebar-section-label">Support</p>

          <button type="button" className="sidebar-nav-item">
            <span className="sidebar-nav-icon">
              <Icon name="settings" />
            </span>
            <span>Settings</span>
          </button>

          <button type="button" className="sidebar-nav-item">
            <span className="sidebar-nav-icon">
              <Icon name="help" />
            </span>
            <span>Help</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Local processing</span>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar-context">
            <span className="topbar-context-label">TalentMatch</span>
            <span className="topbar-context-divider">/</span>
            <span>
              {activePage === 'setup' && 'Screening Setup'}
              {activePage === 'dashboard' && 'Candidate Dashboard'}
              {activePage === 'review' && 'Candidate Review'}
              {activePage === 'comparison' && 'Candidate Comparison'}
            </span>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="topbar-icon-button"
              aria-label="Notifications"
            >
              <Icon name="bell" size={17} />
            </button>

            <div className="user-menu">
              <div className="user-avatar">R</div>

              <div className="user-details">
                <strong>Recruiter</strong>
                <span>Workspace</span>
              </div>
            </div>
          </div>
        </header>

        <main className="workspace">{children}</main>
      </div>
    </div>
  )
}

export default RecruiterLayout