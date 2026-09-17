import { useState } from 'react'

import './App.css'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RecruiterLayout, {
  type RecruiterPage,
} from './layouts/RecruiterLayout'
import ScreeningSetup from './pages/ScreeningSetup'
import CandidateDashboard from './pages/CandidateDashboard'
import CandidateReview from './pages/CandidateReview'
import CandidateComparison from './pages/CandidateComparison'
import History from './pages/History'

type Page =
  | 'landing'
  | 'login'
  | RecruiterPage

function App() {
  const [page, setPage] = useState<Page>('landing')
  const [activeJobId, setActiveJobId] =
    useState<number | null>(null)
  const [selectedCandidateId, setSelectedCandidateId] =
    useState<string | null>(null)

  const startNewScreening = () => {
    setActiveJobId(null)
    setSelectedCandidateId(null)
    setPage('setup')
  }

  const continueWithoutLogin = () => {
    setActiveJobId(null)
    setSelectedCandidateId(null)
    setPage('setup')
  }

  if (page === 'landing') {
    return (
      <LandingPage
        onLogin={() => setPage('login')}
        onContinueWithoutLogin={continueWithoutLogin}
      />
    )
  }

  if (page === 'login') {
    return (
      <LoginPage
        onLoginSuccess={() => {
          setActiveJobId(null)
          setSelectedCandidateId(null)
          setPage('setup')
        }}
        onBack={() => setPage('landing')}
      />
    )
  }

  return (
    <RecruiterLayout
      activePage={page}
      onNavigate={setPage}
      onNewScreening={startNewScreening}
    >
      {page === 'setup' && (
        <ScreeningSetup
          onScreeningComplete={(job) => {
            setActiveJobId(job.job.id)
            setPage('dashboard')
          }}
        />
      )}

      {page === 'dashboard' && (
        <CandidateDashboard
          jobId={activeJobId}
          onCandidateSelect={(candidateId) => {
            setSelectedCandidateId(candidateId)
            setPage('review')
          }}
        />
      )}

      {page === 'review' && (
        <CandidateReview
          jobId={activeJobId}
          candidateId={selectedCandidateId}
          onBack={() => setPage('dashboard')}
        />
      )}

      {page === 'comparison' && (
        <CandidateComparison
          jobId={activeJobId}
          onBack={() => setPage('dashboard')}
        />
      )}

      {page === 'history' && (
        <History
          onOpenScreening={(jobId) => {
            setActiveJobId(jobId)
            setSelectedCandidateId(null)
            setPage('dashboard')
          }}
        />
      )}
    </RecruiterLayout>
  )
}

export default App