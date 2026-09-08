const TOPIC_COLORS = {
  'Monetary Policy': '#3B82F6',
  'Financial Stability': '#14B8A6',
  'Digital Finance': '#8B5CF6',
  'AI in Banking': '#F59E0B',
}

function TopicBars({ data }) {
  const entries = Object.entries(data)
  const total = entries.reduce((sum, [, count]) => sum + count, 0)
  const maxCount = Math.max(...entries.map(([, count]) => count), 1)

  return (
    <div className="topic-bars">
      {entries.map(([topic, count]) => (
        <div key={topic} className="topic-bar-row">
          <div className="topic-bar-label">{topic}</div>
          <div className="topic-bar-track">
            <div
              className="topic-bar-fill"
              style={{
                width: `${(count / maxCount) * 100}%`,
                background: TOPIC_COLORS[topic] || '#94A3B8',
              }}
            />
          </div>
          <div className="topic-bar-pct">{Math.round((count / total) * 100)}%</div>
        </div>
      ))}
    </div>
  )
}

export default TopicBars
