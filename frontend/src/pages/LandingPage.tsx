interface LandingPageProps {
    onLogin: () => void
}

function LandingPage({ onLogin }: LandingPageProps) {
    return (
        <main className="landing-page">
            <header className="landing-header">
                <a href="/" className="landing-logo">
                    <span className="landing-logo-mark">T</span>

                    <span>
                        <strong>TalentMatch</strong>
                        <small>AI</small>
                    </span>
                </a>

                <nav className="landing-nav" aria-label="Main navigation">
                    <a href="#how-it-works">How it works</a>
                    <a href="#why-talentmatch">Why TalentMatch</a>
                </nav>

                <button
                    type="button"
                    className="landing-login-button"
                    onClick={onLogin}
                >
                    Log in
                </button>
            </header>

            <section className="landing-hero">
                <div className="landing-hero-content">
                    <span className="landing-eyebrow">
                        Evidence-based candidate screening
                    </span>

                    <h1>
                        Find the right candidates.
                        <span> See why they match.</span>
                    </h1>

                    <p className="landing-hero-description">
                        TalentMatch helps recruiters screen resumes against job
                        requirements using transparent matching, structured evidence, and
                        deterministic scoring.
                    </p>

                    <div className="landing-hero-actions">
                        <button
                            type="button"
                            className="landing-primary-button"
                            onClick={onLogin}
                        >
                            Start screening
                            <span aria-hidden="true">→</span>
                        </button>

                        <a href="#how-it-works" className="landing-secondary-button">
                            See how it works
                        </a>
                    </div>

                    <div className="landing-hero-note">
                        <span className="landing-note-dot" />
                        Built for recruiters. Designed around evidence.
                    </div>
                </div>

                <div className="landing-product-area">
                    <div className="landing-accent-block landing-accent-block-left" />
                    <div className="landing-accent-block landing-accent-block-top" />

                    <div className="landing-product-card">
                        <div className="product-card-header">
                            <div>
                                <span className="product-card-label">SCREENING RESULT</span>
                                <strong>Senior Python Engineer</strong>
                            </div>

                            <span className="product-card-status">Processed</span>
                        </div>

                        <div className="product-card-candidate">
                            <div className="candidate-avatar">AO</div>

                            <div className="candidate-details">
                                <strong>Amara Okafor</strong>
                                <span>Candidate-001</span>
                            </div>

                            <div className="candidate-score">
                                <strong>91%</strong>
                                <span>Strong match</span>
                            </div>
                        </div>

                        <div className="product-card-divider" />

                        <div className="product-card-section">
                            <div className="product-section-heading">
                                <span>Required skills</span>
                                <strong>4 / 4</strong>
                            </div>

                            <div className="product-skill-list">
                                <span className="product-skill matched">Python</span>
                                <span className="product-skill matched">FastAPI</span>
                                <span className="product-skill matched">SQL</span>
                                <span className="product-skill matched">REST APIs</span>
                            </div>
                        </div>

                        <div className="product-card-section">
                            <div className="product-section-heading">
                                <span>Score breakdown</span>
                                <span className="product-section-muted">/ 100</span>
                            </div>

                            <div className="product-score-list">
                                <div className="product-score-row">
                                    <span>Required skills</span>
                                    <div>
                                        <i style={{ width: '95%' }} />
                                    </div>
                                    <strong>38</strong>
                                </div>

                                <div className="product-score-row">
                                    <span>Experience</span>
                                    <div>
                                        <i style={{ width: '92%' }} />
                                    </div>
                                    <strong>23</strong>
                                </div>

                                <div className="product-score-row">
                                    <span>Responsibilities</span>
                                    <div>
                                        <i style={{ width: '93%' }} />
                                    </div>
                                    <strong>14</strong>
                                </div>
                            </div>
                        </div>

                        <div className="product-evidence">
                            <div className="product-evidence-heading">
                                <span className="evidence-icon">✓</span>
                                <span>Evidence found in resume</span>
                            </div>

                            <p>
                                “Developed REST APIs using FastAPI for a production web
                                application.”
                            </p>
                        </div>

                        <div className="product-card-footer">
                            <span>Matching engine</span>
                            <strong>Deterministic</strong>
                        </div>
                    </div>

                    <div className="landing-floating-card">
                        <span>LLM explanation</span>
                        <strong>Grounded in evidence</strong>
                    </div>
                </div>
            </section>

            <section className="landing-proof">
                <div>
                    <strong>10+</strong>
                    <span>resumes screened in batch</span>
                </div>

                <div>
                    <strong>100%</strong>
                    <span>evidence-oriented scoring</span>
                </div>

                <div>
                    <strong>5</strong>
                    <span>matching dimensions</span>
                </div>

                <div>
                    <strong>Human</strong>
                    <span>review remains essential</span>
                </div>
            </section>

            <section id="how-it-works" className="landing-section">
                <div className="landing-section-intro">
                    <span className="landing-eyebrow">How it works</span>

                    <h2>
                        From job description
                        <br />
                        to evidence-backed shortlist.
                    </h2>

                    <p>
                        TalentMatch separates the work of matching from the work of
                        explaining, giving recruiters a clearer basis for reviewing
                        candidates.
                    </p>
                </div>

                <div className="landing-process">
                    <article className="landing-process-item">
                        <span className="process-number">01</span>

                        <h3>Define the role</h3>

                        <p>
                            Upload or paste a job description and identify the requirements,
                            responsibilities, experience, education, and preferred skills.
                        </p>
                    </article>

                    <article className="landing-process-item">
                        <span className="process-number">02</span>

                        <h3>Screen resumes</h3>

                        <p>
                            Process multiple resumes and match candidates using exact,
                            normalized, and semantic signals across the defined criteria.
                        </p>
                    </article>

                    <article className="landing-process-item">
                        <span className="process-number">03</span>

                        <h3>Review the evidence</h3>

                        <p>
                            Inspect scores, matched skills, skill gaps, and resume evidence
                            before making your own hiring decision.
                        </p>
                    </article>
                </div>
            </section>

            <section id="why-talentmatch" className="landing-evidence-section">
                <div className="landing-evidence-copy">
                    <span className="landing-eyebrow">Why TalentMatch</span>

                    <h2>
                        The score tells you
                        <span> where to look.</span>
                    </h2>

                    <p>
                        A candidate score should never be a black box. TalentMatch breaks
                        the result into the factors that contributed to the match and
                        connects those factors back to available resume evidence.
                    </p>

                    <div className="landing-principles">
                        <div>
                            <span>01</span>
                            <div>
                                <strong>Deterministic matching</strong>
                                <p>
                                    The matching engine owns candidate scoring and ranking.
                                </p>
                            </div>
                        </div>

                        <div>
                            <span>02</span>
                            <div>
                                <strong>Grounded explanations</strong>
                                <p>
                                    The LLM explains results using evidence supplied by the
                                    matching engine.
                                </p>
                            </div>
                        </div>

                        <div>
                            <span>03</span>
                            <div>
                                <strong>Human judgment</strong>
                                <p>
                                    TalentMatch supports recruiter decisions rather than making
                                    hiring decisions for them.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="landing-evidence-visual">
                    <div className="evidence-visual-header">
                        <span>Candidate analysis</span>
                        <span>91%</span>
                    </div>

                    <div className="evidence-visual-line" />

                    <div className="evidence-visual-item">
                        <span className="evidence-check">✓</span>

                        <div>
                            <strong>Python</strong>
                            <p>Direct experience found</p>
                        </div>

                        <span className="evidence-match">Matched</span>
                    </div>

                    <div className="evidence-visual-item">
                        <span className="evidence-check">✓</span>

                        <div>
                            <strong>FastAPI</strong>
                            <p>Production API experience found</p>
                        </div>

                        <span className="evidence-match">Matched</span>
                    </div>

                    <div className="evidence-visual-item">
                        <span className="evidence-gap">—</span>

                        <div>
                            <strong>AWS</strong>
                            <p>No evidence found in resume</p>
                        </div>

                        <span className="evidence-missing">Missing</span>
                    </div>

                    <div className="evidence-visual-footer">
                        <span>Explanation</span>
                        <p>
                            Strong technical alignment with one identified skill gap.
                        </p>
                    </div>
                </div>
            </section>

            <footer className="landing-footer">
                <div className="landing-logo">
                    <span className="landing-logo-mark">T</span>

                    <span>
                        <strong>TalentMatch</strong>
                        <small>AI</small>
                    </span>
                </div>

                <span>Evidence-based candidate screening.</span>
            </footer>
        </main>
    )
}

export default LandingPage