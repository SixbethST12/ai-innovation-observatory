import { useState, useEffect } from 'react'
import { getPublications, searchPublications } from '../api'
import PublicationCard from './PublicationCard'

const INSTITUTIONS = ['All', 'BIS', 'World Bank', 'Central Bank of Kenya', 'IMF']

function PublicationsView() {
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [institution, setInstitution] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeSearch, setActiveSearch] = useState('')

  useEffect(() => {
    setLoading(true)
    setError(null)

    const request = activeSearch
      ? searchPublications(activeSearch, 20)
      : getPublications({
          limit: 20,
          institution: institution === 'All' ? undefined : institution,
        })

    request
      .then((data) => {
        setPublications(data.results)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [institution, activeSearch])

  function handleSearchSubmit(e) {
    e.preventDefault()
    setActiveSearch(searchQuery.trim())
  }

  function clearSearch() {
    setSearchQuery('')
    setActiveSearch('')
  }

  return (
    <div>
      <form className="search-bar" onSubmit={handleSearchSubmit}>
        <input
          type="text"
          placeholder="Search publications..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button type="submit">Search</button>
        {activeSearch && (
          <button type="button" className="clear-btn" onClick={clearSearch}>Clear</button>
        )}
      </form>

      {!activeSearch && (
        <div className="filter-bar">
          {INSTITUTIONS.map((inst) => (
            <button
              key={inst}
              className={institution === inst ? 'filter-btn active' : 'filter-btn'}
              onClick={() => setInstitution(inst)}
            >
              {inst}
            </button>
          ))}
        </div>
      )}

      {loading && <div className="status">Loading...</div>}
      {error && <div className="status error">Error: {error}</div>}

      {!loading && !error && (
        <>
          <h2>
            {activeSearch ? `Search results for "${activeSearch}"` : 'Recent Publications'}
            {' '}({publications.length})
          </h2>
          <div className="publication-list">
            {publications.length === 0 && <p className="status">No results found.</p>}
            {publications.map((pub) => (
              <PublicationCard key={pub.id} pub={pub} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default PublicationsView
