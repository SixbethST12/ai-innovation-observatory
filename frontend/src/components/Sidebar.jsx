import { LayoutDashboard, FileText, TrendingUp } from 'lucide-react'

const NAV_ITEMS = [
  { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'publications', label: 'Publications', icon: FileText },
  { id: 'trends', label: 'Trend Analysis', icon: TrendingUp },
]

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-nav">
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
      </div>
    </aside>
  )
}

export default Sidebar
