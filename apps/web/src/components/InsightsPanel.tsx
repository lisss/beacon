import { useMemo, useState, type CSSProperties } from 'react'
import {
  type InsightsResponse,
  type Resource,
  type ResourceReview,
  markResourceFeedback,
} from '@/lib/api'
import { removeTodoLocal, upsertTodoLocal } from '@/lib/todoStore'

function SectionTitle({
  children,
  prominent = false,
}: {
  children: React.ReactNode
  prominent?: boolean
}) {
  if (prominent) {
    return (
      <h3 className="text-2xl font-bold tracking-tight text-[var(--title)] sm:text-[1.65rem]">
        {children}
      </h3>
    )
  }
  return <h3 className="text-lg font-semibold tracking-tight text-[var(--title-soft)]">{children}</h3>
}

function ResourceLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="font-semibold text-[var(--link)] underline decoration-[var(--link-underline)] decoration-2 underline-offset-4 transition hover:text-[var(--accent)] hover:decoration-[var(--accent)]"
    >
      {children}
    </a>
  )
}

function RatingBadge({ item }: { item: Resource }) {
  if (item.rating == null) return null
  const count =
    item.rating_count != null
      ? ` · ${item.rating_count.toLocaleString()} ${
          item.rating_count === 1 ? 'rating' : 'ratings'
        }`
      : ''
  const tier = item.rating < 2 ? 'low' : item.rating < 4 ? 'mid' : 'high'
  return (
    <span className="rating-badge" data-tier={tier}>
      ★ {item.rating.toFixed(1)}
      {count}
    </span>
  )
}

function FeedbackButtons({
  item,
  hidden,
  onHide,
}: {
  item: Resource
  hidden: boolean
  onHide: (url: string) => void
}) {
  const [busy, setBusy] = useState(false)
  const [saved, setSaved] = useState<'useful' | 'irrelevant' | null>(null)
  if (!item.url || hidden) return null

  async function send(verdict: 'useful' | 'irrelevant') {
    setBusy(true)
    // Persist locally first so Learning TODO updates even if the session cookie fails.
    if (verdict === 'useful') {
      upsertTodoLocal({
        id: `local-${Date.now()}`,
        url: item.url,
        title: item.title,
        provider: item.provider || '',
        kind: item.kind || '',
        verdict: 'useful',
        created_at: new Date().toISOString(),
        done: false,
      })
    } else {
      removeTodoLocal(item.url)
    }
    setSaved(verdict)
    if (verdict === 'irrelevant') onHide(item.url)
    try {
      await markResourceFeedback({
        url: item.url,
        title: item.title,
        provider: item.provider,
        kind: item.kind,
        verdict,
      })
    } catch {
      // Local TODO already updated; server sync is best-effort.
    } finally {
      setBusy(false)
    }
  }

  if (saved === 'useful') {
    return <p className="feedback-saved">Saved to Learning TODO</p>
  }

  return (
    <div className="feedback-actions">
      <button
        type="button"
        disabled={busy}
        onClick={() => void send('useful')}
        className="btn btn-save"
      >
        Save to TODO
      </button>
      <button
        type="button"
        disabled={busy}
        onClick={() => void send('irrelevant')}
        className="btn btn-irrelevant"
      >
        Irrelevant
      </button>
    </div>
  )
}

function Reviews({ reviews }: { reviews?: ResourceReview[] }) {
  if (!reviews?.length) return null
  return (
    <details className="mt-2 group">
      <summary className="cursor-pointer text-xs font-medium text-[var(--link)] list-none [&::-webkit-details-marker]:hidden">
        <span className="underline decoration-[var(--link-underline)] underline-offset-2 group-open:decoration-[var(--accent)]">
          Community comments ({reviews.length})
        </span>
      </summary>
      <ul className="mt-2 space-y-2 border-l-2 border-[var(--accent-soft)] pl-3">
        {reviews.slice(0, 5).map((rev, idx) => (
          <li key={`${rev.source}-${idx}`} className="text-xs text-[var(--muted)]">
            <p className="text-[var(--ink)]">
              {rev.rating != null && (
                <span className="mr-1.5 font-medium text-[var(--ok)]">★ {rev.rating}</span>
              )}
              <span className="font-medium">{rev.author || rev.source}</span>
              {rev.source ? (
                <span className="text-[var(--muted)]"> via {rev.source}</span>
              ) : null}
            </p>
            <p className="mt-0.5 leading-relaxed">{rev.comment}</p>
            {rev.url ? (
              <a
                href={rev.url}
                target="_blank"
                rel="noreferrer"
                className="mt-0.5 inline-block font-medium text-[var(--link)] underline decoration-[var(--link-underline)] underline-offset-2"
              >
                View details
              </a>
            ) : null}
          </li>
        ))}
      </ul>
    </details>
  )
}

function ResourceList({
  title,
  items,
  empty,
  prominent = false,
  hiddenUrls,
  onHide,
  initialLimit,
}: {
  title: string
  items: Resource[]
  empty: string
  prominent?: boolean
  hiddenUrls: Set<string>
  onHide: (url: string) => void
  /** When set, show this many first; rest behind “Want to explore more?” */
  initialLimit?: number
}) {
  const [showMore, setShowMore] = useState(false)
  const visible = items.filter((i) => !hiddenUrls.has(i.url))
  const limit = initialLimit ?? visible.length
  const shown =
    initialLimit != null && !showMore ? visible.slice(0, limit) : visible
  const extra =
    initialLimit != null && !showMore
      ? Math.max(0, visible.length - initialLimit)
      : 0

  return (
    <section>
      <SectionTitle prominent={prominent}>{title}</SectionTitle>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Trusted sources only · best matches first.
      </p>
      {visible.length === 0 ? (
        <p className="mt-2 text-sm text-[var(--muted)]">{empty}</p>
      ) : (
        <>
          <ul className="mt-4 space-y-4">
            {shown.map((item, index) => (
              <li
                key={`${item.kind}-${item.title}-${index}`}
                className="border-b border-[var(--line)] pb-4 last:border-0"
              >
                <div className="flex flex-wrap items-baseline gap-2">
                  <span className="text-xs font-semibold tabular-nums text-[var(--accent)]">
                    #{index + 1}
                  </span>
                  {item.url ? (
                    <ResourceLink href={item.url}>{item.title}</ResourceLink>
                  ) : (
                    <p className="font-semibold text-[var(--title-soft)]">{item.title}</p>
                  )}
                  <RatingBadge item={item} />
                </div>
                <p className="mt-1 text-sm text-[var(--muted)]">
                  {[item.provider, item.description].filter(Boolean).join(' — ')}
                </p>
                {item.estimated_hours != null && (
                  <p className="mt-1 text-xs font-medium text-[var(--ok)]">
                    ~{item.estimated_hours}h estimated
                  </p>
                )}
                {item.study_tip ? (
                  <p className="mt-1.5 text-xs leading-relaxed text-[var(--ink)]/80">
                    {item.study_tip}
                  </p>
                ) : null}
                <FeedbackButtons
                  item={item}
                  hidden={hiddenUrls.has(item.url)}
                  onHide={onHide}
                />
                <Reviews reviews={item.reviews} />
              </li>
            ))}
          </ul>
          {extra > 0 && (
            <button type="button" onClick={() => setShowMore(true)} className="btn btn-explore">
              Want to explore more? (+{extra})
            </button>
          )}
        </>
      )}
    </section>
  )
}

export function InsightsPanel({
  data,
  showCvGaps = false,
}: {
  data: InsightsResponse
  showCvGaps?: boolean
}) {
  const [showMoreCurriculum, setShowMoreCurriculum] = useState(false)
  const [showMoreRoadmap, setShowMoreRoadmap] = useState(false)
  const [hiddenUrls, setHiddenUrls] = useState<Set<string>>(() => new Set())

  const maxImportance = Math.max(...data.requirements.map((s) => s.percentage), 1)
  const matched = new Set(data.matched_skills ?? [])
  const partial = new Set(data.partial_skills ?? [])
  const stackSkills = [
    ...(data.matched_skills ?? []),
    ...(data.unmatched_cv_skills ?? []),
  ]

  const curriculum = useMemo(() => {
    const base = data.curriculum ?? []
    if (!showMoreCurriculum) return base
    return [...base, ...(data.curriculum_more ?? [])]
  }, [data.curriculum, data.curriculum_more, showMoreCurriculum])

  const roadmap = useMemo(() => {
    const base = data.roadmap ?? []
    if (!showMoreRoadmap) return base
    return [...base, ...(data.roadmap_more ?? [])]
  }, [data.roadmap, data.roadmap_more, showMoreRoadmap])

  const curriculumExtra = data.curriculum_more?.length ?? 0
  const roadmapExtra = data.roadmap_more?.length ?? 0

  function coverageOf(skill: string): 'covered' | 'partial' | 'missing' | null {
    if (!showCvGaps) return null
    if (matched.has(skill)) return 'covered'
    if (partial.has(skill)) return 'partial'
    return 'missing'
  }

  function coverageLabel(status: 'covered' | 'partial' | 'missing') {
    if (status === 'covered') return 'covered'
    if (status === 'partial') return 'partial'
    return 'missing'
  }

  function hideUrl(url: string) {
    setHiddenUrls((prev) => new Set(prev).add(url))
  }

  return (
    <div className="space-y-10">
      <div>
        <p className="text-sm font-medium text-[var(--accent)]">Position</p>
        <h2 className="text-2xl font-semibold tracking-tight text-[var(--title)] sm:text-3xl">
          {data.query}
        </h2>
      </div>

      {showCvGaps && stackSkills.length > 0 && (
        <div className="rounded-lg border border-[var(--line)] bg-white px-5 py-4 shadow-[var(--shadow-section)] sm:px-6">
          <p className="text-sm text-[var(--ink)]">
            Learning path personalized for:{' '}
            <span className="font-medium text-[var(--accent)]">{stackSkills.join(', ')}</span>
          </p>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Materials mix your stack with what this role typically still needs.
          </p>
        </div>
      )}

      <div className={`grid gap-8 ${showCvGaps ? 'lg:grid-cols-2' : ''}`}>
        <section>
          <SectionTitle prominent>Role requirements</SectionTitle>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {showCvGaps
              ? 'Green = covered, yellow = related skill, red = still missing.'
              : 'Typical skills for this position, ranked by importance.'}
          </p>
          <ul className="mt-4 space-y-3">
            {data.requirements.map((skill) => {
              const status = coverageOf(skill.skill)
              const pct = `${(skill.percentage / maxImportance) * 100}%`
              return (
                <li key={skill.skill}>
                  <div className="mb-1 flex justify-between gap-3 text-sm">
                    <span className="font-medium text-[var(--title-soft)]">
                      {skill.skill}
                      {status && (
                        <span className="coverage-label" data-status={status}>
                          {coverageLabel(status)}
                        </span>
                      )}
                    </span>
                    <span className="shrink-0 text-[var(--muted)]">{skill.percentage}%</span>
                  </div>
                  <div className="skill-bar-track">
                    <div
                      className="skill-bar"
                      data-status={status ?? undefined}
                      style={{ '--skill-pct': pct } as CSSProperties}
                    />
                  </div>
                </li>
              )
            })}
          </ul>
        </section>

        {showCvGaps && (
          <section>
            <SectionTitle>Still to learn for this role</SectionTitle>
            {data.missing_skills.length === 0 ? (
              <p className="mt-3 text-sm text-[var(--muted)]">
                No major role gaps — focus on deepening your stack below.
              </p>
            ) : (
              <ul className="mt-4 flex flex-wrap gap-2">
                {data.missing_skills.map((skill) => (
                  <li
                    key={skill.skill}
                    className="rounded-lg border border-[var(--line)] bg-white px-3 py-1.5 text-sm"
                  >
                    <span className="font-medium text-[var(--title-soft)]">{skill.skill}</span>
                    <span className="ml-2 text-[var(--muted)]">{skill.percentage}%</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}
      </div>

      {curriculum.length > 0 && (
        <section className="rounded-lg border border-[var(--line)] bg-white px-6 py-7 shadow-[var(--shadow-section)] sm:px-8">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <SectionTitle prominent>Brief curriculum</SectionTitle>
            <p className="text-sm text-[var(--muted)]">
              ~{data.estimated_study_hours}h total plan
            </p>
          </div>
          <p className="mt-2 text-sm text-[var(--muted)]">
            How to structure learning through the top trusted resources — time boxes and focus
            order.
          </p>
          <ol className="mt-6 space-y-5">
            {curriculum.map((item) => (
              <li key={item.order} className="grid gap-2 sm:grid-cols-[2.5rem_1fr]">
                <span className="text-lg font-semibold text-[var(--accent)]">
                  {String(item.order).padStart(2, '0')}
                </span>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-[var(--accent)]">
                    {item.phase}
                  </p>
                  <p className="mt-0.5 font-semibold text-[var(--title-soft)]">{item.focus}</p>
                  <p className="mt-1 text-sm text-[var(--muted)]">~{item.hours}h</p>
                  <p className="mt-1 text-sm leading-relaxed text-[var(--ink)]/85">
                    {item.structure}
                  </p>
                  {item.resource_titles?.length > 0 && (
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      Materials: {item.resource_titles.join(' · ')}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ol>
          {!showMoreCurriculum && curriculumExtra > 0 && (
            <button
              type="button"
              onClick={() => setShowMoreCurriculum(true)}
              className="btn btn-explore"
            >
              Want to explore more? (+{Math.min(curriculumExtra, 10)} phases)
            </button>
          )}
        </section>
      )}

      <section className="rounded-lg border border-[var(--line)] bg-white px-6 py-7 shadow-[var(--shadow-section)] sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <SectionTitle prominent>Learning roadmap</SectionTitle>
          <p className="text-sm text-[var(--muted)]">
            ~{data.estimated_study_hours} hours estimated
          </p>
        </div>
        <p className="mt-2 text-sm text-[var(--muted)]">
          {showCvGaps
            ? 'Starts from your skills, then covers role gaps.'
            : 'Based on typical requirements for this role.'}
        </p>
        <ol className="mt-6 space-y-5">
          {roadmap.map((step) => (
            <li key={step.order} className="grid gap-2 sm:grid-cols-[2.5rem_1fr]">
              <span className="text-lg font-semibold text-[var(--accent)]">
                {String(step.order).padStart(2, '0')}
              </span>
              <div>
                <p className="font-semibold text-[var(--title-soft)]">{step.title}</p>
                <p className="text-sm text-[var(--muted)]">
                  {step.skills.join(' · ')} · ~{step.estimated_hours}h
                </p>
                {step.how_to ? (
                  <p className="mt-1 text-sm leading-relaxed text-[var(--ink)]/80">
                    {step.how_to}
                  </p>
                ) : null}
                {step.resources?.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {step.resources
                      .filter((r) => !hiddenUrls.has(r.url))
                      .slice(0, 3)
                      .map((r) => (
                        <li key={r.title} className="text-xs text-[var(--muted)]">
                          {r.url ? (
                            <ResourceLink href={r.url}>{r.title}</ResourceLink>
                          ) : (
                            r.title
                          )}
                          {r.estimated_hours != null ? ` · ~${r.estimated_hours}h` : ''}
                          <FeedbackButtons
                            item={r}
                            hidden={hiddenUrls.has(r.url)}
                            onHide={hideUrl}
                          />
                        </li>
                      ))}
                  </ul>
                )}
              </div>
            </li>
          ))}
        </ol>
        {!showMoreRoadmap && roadmapExtra > 0 && (
          <button
            type="button"
            onClick={() => setShowMoreRoadmap(true)}
            className="btn btn-explore"
          >
            Want to explore more? (+{Math.min(roadmapExtra, 10)} steps)
          </button>
        )}
      </section>

      <div className="grid gap-10 md:grid-cols-2">
        <ResourceList
          title="Books"
          items={data.books}
          empty="No trusted books matched this role and skill mix yet."
          prominent
          initialLimit={5}
          hiddenUrls={hiddenUrls}
          onHide={hideUrl}
        />
        <ResourceList
          title="Courses"
          items={data.courses}
          empty="No trusted courses matched this role and skill mix yet."
          prominent
          initialLimit={5}
          hiddenUrls={hiddenUrls}
          onHide={hideUrl}
        />
        <ResourceList
          title="Certifications"
          items={data.certifications}
          empty="No trusted certifications matched this role and skill mix."
          hiddenUrls={hiddenUrls}
          onHide={hideUrl}
        />
        <ResourceList
          title="Interview questions"
          items={data.interview_questions}
          empty="No interview prompts yet."
          hiddenUrls={hiddenUrls}
          onHide={hideUrl}
        />
      </div>
    </div>
  )
}
