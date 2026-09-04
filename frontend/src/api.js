const API_BASE = 'http://localhost:8000'

export async function getPublications({ limit = 10, offset = 0, topic, institution } = {}) {
  const params = new URLSearchParams({ limit, offset })
  if (topic) params.set('topic', topic)
  if (institution) params.set('institution', institution)

  const res = await fetch(`${API_BASE}/publications?${params}`)
  if (!res.ok) throw new Error(`API returned ${res.status}`)
  return res.json()
}

export async function searchPublications(query, limit = 20) {
  const params = new URLSearchParams({ q: query, limit })
  const res = await fetch(`${API_BASE}/search?${params}`)
  if (!res.ok) throw new Error(`API returned ${res.status}`)
  return res.json()
}

export async function getTrends(emergingOnly = false) {
  const params = new URLSearchParams({ emerging_only: emergingOnly })
  const res = await fetch(`${API_BASE}/trends?${params}`)
  if (!res.ok) throw new Error(`API returned ${res.status}`)
  return res.json()
}
