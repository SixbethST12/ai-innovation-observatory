import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { getStats, getPublications } from '../api'
import StatCard from './StatCard'
import PublicationCard from './PublicationCard'

function OverviewPage() {
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getStats(), getPublications({ limit: 5 })])
      .then(([statsData, pubsData]) => {
        setStats(statsData)
        setRecent(pubsData.results)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="status">Loading overview...</div>
  if (error) return <div className="status error">Error: {error}</div>

  const chartData = Object.entries(stats.by_institution)
    .filter(([name]) => name !== 'TEST')
    .map(([name, count]) => ({ name, count }))

  return (
    <div>
      <div className="stat-grid">
        <StatCard label="Total Publications" value={stats.total_publications} />
        <StatCard label="AI Processed" value={stats.processed} />
        <StatCard label="Awaiting Processing" value={stats.unprocessed} />
        <StatCard label="Emerging Trends" value={stats.emerging_trends} accent />
      </div>

      <div className="chart-section">
        <h2>Publications by Source</h2>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#DDD6C4" />
            <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#5B6178' }} />
            <YAxis tick={{ fontSize: 12, fill: '#5B6178' }} />
            <Tooltip />
            <Bar dataKey="count" fill="#A9812F" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="recent-section">
        <h2>Recent Publications</h2>
        <div className="publication-list">
          {recent.map((pub) => (
            <PublicationCard key={pub.id} pub={pub} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default OverviewPage
