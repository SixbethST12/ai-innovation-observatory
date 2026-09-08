import { useState } from 'react'
import { Search } from 'lucide-react'

function Navbar({ onSearch }) {
  const [query, setQuery] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }

  return (
    <header className="navbar">
      <div className="navbar-brand">
        <div className="brand-icon">AI</div>
        <div>
          <h1>AI Innovation Observatory</h1>
          <p>for Central Banking &amp; Financial Sector Intelligence</p>
        </div>
      </div>

      <form className="navbar-search" onSubmit={handleSubmit}>
        <Search size={16} className="search-icon" />
        <input
          type="text"
          placeholder="Search publications, topics..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </form>
    </header>
  )
}

export default Navbar
