function PublicationCard({ pub }) {
  return (
    <div className="publication-card">
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
  )
}

export default PublicationCard
