import { useState, type ReactNode } from 'react'
import { SectionIcon, type SectionIconName } from '@/components/SectionIcons'
import { isSectionOpen, setSectionOpen } from '@/lib/sectionCollapseStore'

export function CollapsibleSection({
  id,
  title,
  icon,
  summary,
  meta,
  defaultOpen = false,
  children,
}: {
  id: string
  title: string
  icon?: SectionIconName
  /** Short teaser shown while collapsed */
  summary?: ReactNode
  /** Right-side meta (e.g. hours) always visible in the header */
  meta?: ReactNode
  /** Initial open state when the user has never toggled this section */
  defaultOpen?: boolean
  children: ReactNode
}) {
  const [open, setOpen] = useState(() => isSectionOpen(id, defaultOpen))

  function toggle() {
    setOpen((prev) => {
      const next = !prev
      setSectionOpen(id, next)
      return next
    })
  }

  return (
    <section
      data-section={id}
      className={`collapse-section ${open ? 'collapse-section--open' : ''}`.trim()}
    >
      <button
        type="button"
        className="collapse-header"
        onClick={toggle}
        aria-expanded={open}
        aria-controls={`section-body-${id}`}
      >
        <span className="collapse-header-main">
          {icon ? <SectionIcon name={icon} /> : null}
          <span className="collapse-title">{title}</span>
          <span className="collapse-chevron" aria-hidden>
            {open ? '▾' : '▸'}
          </span>
        </span>
        {meta ? <span className="collapse-meta">{meta}</span> : null}
      </button>
      {!open && summary ? (
        <p className="collapse-summary">{summary}</p>
      ) : null}
      {open ? (
        <div id={`section-body-${id}`} className="collapse-body">
          {children}
        </div>
      ) : null}
    </section>
  )
}
