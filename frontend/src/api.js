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

export async function getStats() {
  const res = await fetch(`${API_BASE}/stats`)
  if (!res.ok) throw new Error(`API returned ${res.status}`)
  return res.json()
}

export async function getTopicDistribution() {
  const res = await fetch(`${API_BASE}/stats/topics`)
  if (!res.ok) throw new Error(`API returned ${res.status}`)
  return res.json()
}

export async function getTimeline() {
  const res = await fetch(`${API_BASE}/stats/timeline`)
  if (!res.ok) throw new Error(`API returned ${res.status}`)
  return res.json()
}

export function getRelevance(pub) {
  const val = pub?.relevance ?? pub?.relevance_score ?? null
  return typeof val === 'number' ? val : null
}

// Reads a publication's relevance score if present. Currently always
// returns null/undefined since relevance_score isn't in the backend
// response yet (the numeric scoring work is paused - see relevance.py
// history). This is intentional: the modal correctly shows "not
// scored" rather than a fabricated number, until real scoring exists.
export function getRelevance(pub) {
  return pub?.relevance_score ?? null
}
