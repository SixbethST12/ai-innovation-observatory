import { useState } from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import OverviewPage from './components/OverviewPage'
import PublicationsView from './components/PublicationsView'
import TrendsView from './components/TrendsView'
import ComingSoon from './components/ComingSoon'
import './App.css'

const COMING_SOON_TITLES = {
  reports: 'Intelligence Reports',
  knowledge: 'Knowledge Base',
  alerts: 'Alerts & Notifications',
  settings: 'Settings',
}

function App() {
  const [activePage, setActivePage] = useState('overview')
  const [searchQuery, setSearchQuery] = useState(null)

  function handleNavbarSearch(query) {
    setSearchQuery(query)
    setActivePage('search')
  }

  function handleNavigate(page) {
    setActivePage(page)
    if (page !== 'search') setSearchQuery(null)
  }

  return (
    <div className="app-shell">
      <Navbar onSearch={handleNavbarSearch} />
      <div className="app-body">
        <Sidebar activePage={activePage} onNavigate={handleNavigate} />
        <main className="main-content">
          {activePage === 'overview' && <OverviewPage />}
          {(activePage === 'publications' || activePage === 'search') && (
            <PublicationsView initialSearch={searchQuery} />
          )}
          {activePage === 'trends' && <TrendsView />}
          {COMING_SOON_TITLES[activePage] && (
            <ComingSoon title={COMING_SOON_TITLES[activePage]} />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
