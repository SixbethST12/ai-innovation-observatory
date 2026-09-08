import { useState } from 'react'
import Sidebar from './components/Sidebar'
import OverviewPage from './components/OverviewPage'
import PublicationsView from './components/PublicationsView'
import TrendsView from './components/TrendsView'
import './App.css'

const PAGE_TITLES = {
  overview: 'Overview',
  publications: 'Publications',
  trends: 'Trends',
}

function App() {
  const [activePage, setActivePage] = useState('overview')

  return (
    <div className="dashboard">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      <div className="main-content">
        <div className="content-header">
          <h1>{PAGE_TITLES[activePage]}</h1>
        </div>

        <div className="content-body">
          {activePage === 'overview' && <OverviewPage />}
          {activePage === 'publications' && <PublicationsView />}
          {activePage === 'trends' && <TrendsView />}
        </div>
      </div>
    </div>
  )
}

export default App
