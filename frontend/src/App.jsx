import { useState } from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import OverviewPage from './components/OverviewPage'
import PublicationsView from './components/PublicationsView'
import TrendsView from './components/TrendsView'
import './App.css'

function App() {
  const [activePage, setActivePage] = useState('overview')
  const [searchQuery, setSearchQuery] = useState(null)

  function handleNavbarSearch(query) {
    setSearchQuery(query)
    setActivePage('publications')
  }

  return (
    <div className="app-shell">
      <Navbar onSearch={handleNavbarSearch} />
      <div className="app-body">
        <Sidebar activePage={activePage} onNavigate={(page) => { setActivePage(page); setSearchQuery(null) }} />
        <main className="main-content">
          {activePage === 'overview' && <OverviewPage />}
          {activePage === 'publications' && <PublicationsView initialSearch={searchQuery} />}
          {activePage === 'trends' && <TrendsView />}
        </main>
      </div>
    </div>
  )
}

export default App
