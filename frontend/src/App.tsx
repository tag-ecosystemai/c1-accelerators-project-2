import './App.css'

function App() {
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

        <section className="setup-grid">
          <article className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Step 01</p>
                <h2>Screening Setup</h2>
              </div>
              <span className="panel-status">Not started</span>
            </div>

            <div className="empty-state">
              <div className="empty-icon">JD</div>
              <h3>Start with a job description</h3>
              <p>
                Upload a job description or paste it directly. TalentMatch
                will extract requirements, preferred skills, experience,
                education, and responsibilities.
              </p>
              <button type="button" className="secondary-button">
                Add job description
              </button>
            </div>
          </article>

          <article className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Step 02</p>
                <h2>Candidate Pool</h2>
              </div>
              <span className="panel-status">Waiting for JD</span>
            </div>

            <div className="empty-state">
              <div className="empty-icon">CV</div>
              <h3>Upload candidate resumes</h3>
              <p>
                Add resumes in PDF, DOCX, or TXT format. Batch processing
                will parse each candidate and prepare them for matching.
              </p>
              <button type="button" className="secondary-button" disabled>
                Add resumes
              </button>
            </div>
          </article>
        </section>

        <section className="principles">
          <div>
            <p className="panel-kicker">How TalentMatch works</p>
            <h2>The engine ranks. The LLM explains.</h2>
          </div>

          <div className="principle-list">
            <div className="principle">
              <span>01</span>
              <p>
                Deterministic scoring combines skills, experience,
                responsibilities, education, and preferred requirements.
              </p>
            </div>

            <div className="principle">
              <span>02</span>
              <p>
                Semantic matching supplements explicit skill matching without
                replacing transparent evidence.
              </p>
            </div>

            <div className="principle">
              <span>03</span>
              <p>
                Groq generates grounded explanations from the evidence
                produced by the matching engine.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
