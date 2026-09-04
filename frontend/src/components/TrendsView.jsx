import { useState, useEffect } from 'react'
import { getTrends } from '../api'

function TrendsView() {
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [emergingOnly, setEmergingOnly] = useState(true)

  useEffect(() => {
    setLoading(true)
    getTrends(emergingOnly)
      .then((data) => {
        setTrends(data.results)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [emergingOnly])

  return (
    <div>
      <div className="filter-bar">
        <button
          className={emergingOnly ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setEmergingOnly(true)}
        >
          Emerging Only
        </button>
        <button
          className={!emergingOnly ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setEmergingOnly(false)}
        >
          All Trends
        </button>
      </div>

      {loading && <div className="status">Loading...</div>}
      {error && <div className="status error">Error: {error}</div>}

      {!loading && !error && (
        <>
          <h2>Topic Trends ({trends.length})</h2>
          {trends.length === 0 && <p className="status">No trend data yet.</p>}
          <div className="trend-list">
            {trends.map((t, i) => (
              <div key={i} className={t.is_emerging ? 'trend-card emerging' : 'trend-card'}>
                <div className="trend-topic">
                  {t.topic}
                  {t.is_emerging && <span className="emerging-badge">EMERGING</span>}
                </div>
                <div className="trend-detail">
                  {t.time_window} — {t.publication_count} publication{t.publication_count !== 1 ? 's' : ''}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default TrendsView
