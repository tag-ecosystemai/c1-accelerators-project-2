import { useState } from 'react'
import './App.css'
import RecruiterLayout from './layouts/RecruiterLayout'
import ScreeningSetup from './pages/ScreeningSetup'
import CandidateDashboard from './pages/CandidateDashboard'
import CandidateReview from './pages/CandidateReview'
import CandidateComparison from './pages/CandidateComparison'

type Page = 'setup' | 'dashboard' | 'review' | 'comparison'

function App() {
  const [page, setPage] = useState<Page>('setup')

  const [selectedCandidateId, setSelectedCandidateId] = useState<
    string | null
  >(null)

  return (
    <RecruiterLayout
      activePage={page}
      onNavigate={setPage}
    >
      {page === 'setup' && (
        <ScreeningSetup
          onScreeningComplete={() => setPage('dashboard')}
        />
      )}

      {page === 'dashboard' && (
        <CandidateDashboard
          onCandidateSelect={(candidateId) => {
            setSelectedCandidateId(candidateId)
            setPage('review')
          }}
        />
      )}

      {page === 'review' && (
        <CandidateReview
          candidateId={selectedCandidateId}
          onBack={() => setPage('dashboard')}
        />
      )}

      {page === 'comparison' && (
        <CandidateComparison
          onBack={() => setPage('dashboard')}
        />
      )}
    </RecruiterLayout>
  )
}

export default App