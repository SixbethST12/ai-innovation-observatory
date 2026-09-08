import { LayoutDashboard, FileText, TrendingUp } from 'lucide-react'

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'publications', label: 'Publications', icon: FileText },
  { id: 'trends', label: 'Trends', icon: TrendingUp },
]

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>AI Observatory</h1>
        <p>Bank of Tanzania</p>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={activePage === id ? 'nav-item active' : 'nav-item'}
            onClick={() => onNavigate(id)}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p>Central Banking &amp; Financial Sector Intelligence</p>
      </div>
    </aside>
  )
}

export default Sidebar
