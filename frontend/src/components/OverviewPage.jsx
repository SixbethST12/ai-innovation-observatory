import { useState, useEffect } from 'react'
import { FileText, CheckCircle2, Building2, Lightbulb } from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { getStats, getPublications, getTrends, getTopicDistribution, getTimeline } from '../api'
import StatCard from './StatCard'
import PublicationCard from './PublicationCard'
import TopicBars from './TopicBars'

const DONUT_COLORS = ['#3B82F6', '#8B5CF6', '#14B8A6', '#F59E0B', '#EF4444']

function OverviewPage() {
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [trends, setTrends] = useState([])
  const [topics, setTopics] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      getStats(),
      getPublications({ limit: 5 }),
      getTrends(true),
      getTopicDistribution(),
      getTimeline(),
    ])
      .then(([statsData, pubsData, trendsData, topicsData, timelineData]) => {
        setStats(statsData)
        setRecent(pubsData.results)
        setTrends(trendsData.results)
        setTopics(topicsData)
        setTimeline(timelineData)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="status">Loading overview...</div>
  if (error) return <div className="status error">Error: {error}</div>

  const institutionData = Object.entries(stats.by_institution)
    .filter(([name]) => name !== 'TEST')
    .map(([name, value]) => ({ name, value }))

  const timelineData = Object.entries(timeline).map(([month, count]) => ({ month, count }))

  return (
    <div>
      <div className="stat-grid">
        <StatCard label="Total Publications" value={stats.total_publications} icon={FileText} color="blue" />
        <StatCard label="AI Processed" value={stats.processed} icon={CheckCircle2} color="green" />
        <StatCard label="Institutions Tracked" value={institutionData.length} icon={Building2} color="purple" />
        <StatCard label="Emerging Trends" value={stats.emerging_trends} icon={Lightbulb} color="orange" />
      </div>

      <div className="panel-row">
        <div className="panel panel-recent">
          <div className="panel-header"><h2>Recent Publications</h2></div>
          <div className="publication-list compact">
            {recent.map((pub) => (
              <PublicationCard key={pub.id} pub={pub} />
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><h2>Publications by Institution</h2></div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={institutionData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={2}>
                {institutionData.map((_, i) => (
                  <Cell key={i} fill={DONUT_COLORS[i % DONUT_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="legend">
            {institutionData.map((entry, i) => (
              <div key={entry.name} className="legend-item">
                <span className="legend-dot" style={{ background: DONUT_COLORS[i % DONUT_COLORS.length] }} />
                {entry.name}
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><h2>Publications by Topic</h2></div>
          <TopicBars data={topics} />
        </div>
      </div>

      <div className="panel-row">
        <div className="panel">
          <div className="panel-header"><h2>Emerging Trends</h2></div>
          <div className="trend-list">
            {trends.length === 0 && <p className="status">No emerging trends right now.</p>}
            {trends.map((t, i) => (
              <div key={i} className="trend-card emerging">
                <div className="trend-topic">
                  {t.topic}
                  <span className="emerging-badge">EMERGING</span>
                </div>
                <div className="trend-detail">{t.time_window} — {t.publication_count} publications</div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel panel-wide">
          <div className="panel-header"><h2>Publication Timeline</h2></div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748B' }} />
              <YAxis tick={{ fontSize: 12, fill: '#64748B' }} />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

export default OverviewPage
