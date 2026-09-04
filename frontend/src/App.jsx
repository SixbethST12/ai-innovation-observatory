import { useState } from 'react'
import PublicationsView from './components/PublicationsView'
import TrendsView from './components/TrendsView'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('publications')

  return (
    <div className="app">
      <header>
        <h1>AI Innovation Observatory</h1>
        <p className="subtitle">Central Banking &amp; Financial Sector Intelligence — Bank of Tanzania</p>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === 'publications' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('publications')}
        >
          Publications
        </button>
        <button
          className={activeTab === 'trends' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('trends')}
        >
          Trends
        </button>
      </nav>

      <main>
        {activeTab === 'publications' ? <PublicationsView /> : <TrendsView />}
      </main>
    </div>
  )
}

export default App
