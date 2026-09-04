import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/publications?limit=10`)
      .then((res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setPublications(data.results)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="status">Loading publications...</div>
  if (error) return <div className="status error">Error: {error} — is the backend running on port 8000?</div>

  return (
    <div className="app">
      <header>
        <h1>AI Innovation Observatory</h1>
        <p className="subtitle">Central Banking &amp; Financial Sector Intelligence — Bank of Tanzania</p>
      </header>

      <main>
        <h2>Recent Publications ({publications.length})</h2>
        <div className="publication-list">
          {publications.map((pub) => (
            <div key={pub.id} className="publication-card">
              <div className="card-header">
                <span className="institution-badge">{pub.institution}</span>
                {pub.published_date && (
                  <span className="date">{pub.published_date.slice(0, 10)}</span>
                )}
              </div>
              <h3>
                <a href={pub.source_url} target="_blank" rel="noopener noreferrer">
                  {pub.title}
                </a>
              </h3>

              {pub.processed ? (
                <>
                  <p className="summary">{pub.summary}</p>
                  <div className="topics">
                    {pub.topics.map((topic) => (
                      <span key={topic} className="topic-tag">{topic}</span>
                    ))}
                  </div>
                  <p className="ai-disclaimer">{pub.ai_generated_disclaimer}</p>
                </>
              ) : (
                <p className="not-processed">Not yet AI-processed</p>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}

export default App
