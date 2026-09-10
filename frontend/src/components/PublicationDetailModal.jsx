import { useEffect, useRef } from 'react'
import { X, ExternalLink, AlertCircle, Sparkles, Target } from 'lucide-react'
import { getRelevance } from '../api'

function PublicationDetailModal({ pub, onClose }) {
  const panelRef = useRef(null)

  useEffect(() => {
    function handleKey(e) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  useEffect(() => {
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = prev }
  }, [])

  useEffect(() => {
    panelRef.current?.focus()
  }, [])

  if (!pub) return null

  const relevance = getRelevance(pub)

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div
      className="modal-backdrop"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="pub-modal-title"
    >
      <div className="modal-panel" ref={panelRef} tabIndex={-1}>
        <button
          type="button"
          className="modal-close"
          onClick={onClose}
          aria-label="Close"
        >
          <X size={20} />
        </button>

        <header className="modal-header">
          <div className="modal-meta">
            <span className="institution-badge">{pub.institution}</span>
            {pub.document_type && (
              <span className="doc-type-badge">{pub.document_type}</span>
            )}
            {pub.published_date && (
              <span className="date">{pub.published_date.slice(0, 10)}</span>
            )}
          </div>
          <h2 id="pub-modal-title">{pub.title}</h2>
        </header>

        <section className="modal-section">
          <h3><Sparkles size={16} /> AI Summary</h3>
          {pub.processed ? (
            <>
              <p className="summary">{pub.summary}</p>
              <div className="ai-callout">
                <AlertCircle size={14} />
                <span>
                  {pub.ai_generated_disclaimer ||
                    'AI-generated summary. Not an official Bank position. Verify against the original source.'}
                </span>
              </div>
            </>
          ) : (
            <p className="not-processed">Not yet AI-processed</p>
          )}
        </section>

        {pub.topics?.length > 0 && (
          <section className="modal-section">
            <h3>Topics</h3>
            <div className="topics">
              {pub.topics.map((topic) => (
                <span key={topic} className="topic-tag">{topic}</span>
              ))}
            </div>
          </section>
        )}

        <section className="modal-section">
          <h3><Target size={16} /> Relevance to Bank of Tanzania</h3>
          {relevance != null ? (
            <div className="relevance-block">
              <span className="relevance-score">{relevance}</span>
              <span className="relevance-label">
                {relevance >= 0.75
                  ? 'High relevance'
                  : relevance >= 0.4
                  ? 'Moderate relevance'
                  : 'Low relevance'}
              </span>
              <p className="ai-callout">
                <AlertCircle size={14} />
                <span>AI-assisted assessment. Not an official Bank position.</span>
              </p>
            </div>
          ) : (
            <p className="not-processed">Relevance not scored for this publication.</p>
          )}
        </section>

        <footer className="modal-footer">
          <a
            href={pub.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
          >
            <ExternalLink size={16} /> View original source
          </a>
          <span className="source-url">{pub.source_url}</span>
        </footer>
      </div>
    </div>
  )
}

export default PublicationDetailModal
