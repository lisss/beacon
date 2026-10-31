export type SkillStat = {
  skill: string
  count: number
  percentage: number
}

export type ResourceReview = {
  author: string
  rating?: number | null
  comment: string
  url: string
  source: string
}

export type Resource = {
  kind: string
  title: string
  url: string
  provider: string
  skills: string[]
  description: string
  estimated_hours?: number | null
  value_score?: number
  rating?: number | null
  rating_count?: number | null
  reviews?: ResourceReview[]
  study_tip?: string
}

export type RoadmapStep = {
  order: number
  title: string
  skills: string[]
  estimated_hours: number
  how_to?: string
  resources: Resource[]
}

export type CurriculumItem = {
  order: number
  phase: string
  focus: string
  hours: number
  structure: string
  resource_titles: string[]
}

export type InsightsResponse = {
  query: string
  location?: string
  requirements: SkillStat[]
  matched_skills: string[]
  partial_skills: string[]
  missing_skills: SkillStat[]
  unmatched_cv_skills: string[]
  interview_questions: Resource[]
  books: Resource[]
  courses: Resource[]
  certifications: Resource[]
  roadmap: RoadmapStep[]
  curriculum: CurriculumItem[]
  roadmap_more?: RoadmapStep[]
  curriculum_more?: CurriculumItem[]
  estimated_study_hours: number
}

export type StoredCv = {
  id: string
  filename: string
  content_type: string
  uploaded_at: string
  download_url: string
  all_skills: string[]
}

export type FeedbackItem = {
  id: string
  url: string
  title: string
  provider: string
  kind: string
  verdict: 'useful' | 'irrelevant' | string
  created_at: string
}

const API_URL =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? 'http://localhost:8001' : '')

/** Session cookie must travel with CV / feedback requests. */
const withSession: RequestInit = { credentials: 'include' }

export function cvDownloadUrl(): string {
  return `${API_URL}/api/cv/download`
}

export async function fetchInsights(
  input: {
    query: string
    cv_skills: string[]
  },
  options?: { signal?: AbortSignal },
): Promise<InsightsResponse> {
  const res = await fetch(`${API_URL}/api/insights`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: input.query,
      cv_skills: input.cv_skills,
    }),
    signal: options?.signal,
    ...withSession,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Failed to load insights')
  }
  return res.json()
}

export async function markResourceFeedback(input: {
  url: string
  title: string
  provider?: string
  kind?: string
  verdict: 'useful' | 'irrelevant'
}): Promise<FeedbackItem> {
  const res = await fetch(`${API_URL}/api/resources/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
    ...withSession,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Failed to save feedback')
  }
  const data = (await res.json()) as { item: FeedbackItem }
  return data.item
}

export async function removeResourceFeedback(url: string): Promise<void> {
  await fetch(
    `${API_URL}/api/resources/feedback?url=${encodeURIComponent(url)}`,
    { method: 'DELETE', ...withSession },
  )
}

export async function fetchTodoList(): Promise<FeedbackItem[]> {
  const res = await fetch(`${API_URL}/api/resources/todo`, withSession)
  if (!res.ok) return []
  const data = (await res.json()) as { items: FeedbackItem[] }
  return data.items ?? []
}

export async function parseCv(
  file: File,
  role: string,
): Promise<{ skills: string[]; all_skills: string[]; cv: StoredCv | null }> {
  const form = new FormData()
  form.append('file', file)
  const params = new URLSearchParams()
  if (role.trim()) params.set('role', role.trim())
  const qs = params.toString()
  const res = await fetch(`${API_URL}/api/cv/parse${qs ? `?${qs}` : ''}`, {
    method: 'POST',
    body: form,
    ...withSession,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Failed to parse CV')
  }
  const data = (await res.json()) as {
    skills: string[]
    all_skills?: string[]
    cv?: StoredCv
  }
  return {
    skills: data.skills ?? [],
    all_skills: data.all_skills ?? data.skills ?? [],
    cv: data.cv ?? null,
  }
}

export async function fetchCurrentCv(): Promise<StoredCv | null> {
  const res = await fetch(`${API_URL}/api/cv/current`, withSession)
  if (!res.ok) return null
  const data = (await res.json()) as { cv: StoredCv | null }
  return data.cv ?? null
}

export async function deleteCurrentCv(): Promise<void> {
  await fetch(`${API_URL}/api/cv/current`, { method: 'DELETE', ...withSession })
}

export async function filterSkillsForRole(
  role: string,
  skills: string[],
): Promise<string[]> {
  const res = await fetch(`${API_URL}/api/cv/skills/for-role`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, skills }),
    ...withSession,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Failed to filter skills')
  }
  const data = (await res.json()) as { skills: string[] }
  return data.skills ?? []
}

export async function suggestRoles(query: string): Promise<string[]> {
  const res = await fetch(
    `${API_URL}/api/suggest/roles?q=${encodeURIComponent(query)}&limit=12`,
    withSession,
  )
  if (!res.ok) return []
  const data = (await res.json()) as { suggestions: string[] }
  return data.suggestions ?? []
}
