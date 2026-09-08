function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon stat-icon-${color}`}>
        <Icon size={20} />
      </div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}

export default StatCard
