import {
  LayoutDashboard, Search, FileText, FileBarChart,
  TrendingUp, BookOpen, Bell, Settings, Sparkles
} from 'lucide-react'

const NAV_ITEMS = [
  { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'search', label: 'Search & Discover', icon: Search },
  { id: 'publications', label: 'Publications', icon: FileText },
  { id: 'reports', label: 'Intelligence Reports', icon: FileBarChart },
  { id: 'trends', label: 'Trend Analysis', icon: TrendingUp },
  { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
  { id: 'alerts', label: 'Alerts & Notifications', icon: Bell },
  { id: 'settings', label: 'Settings', icon: Settings },
]

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-badge">T</div>
        <div className="logo-text">BANK OF TANZANIA</div>
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

      <div className="sidebar-promo">
        <Sparkles size={20} />
        <p><strong>Smarter Insights</strong><br />for a Stronger Financial Future</p>
      </div>
    </aside>
  )
}

export default Sidebar
