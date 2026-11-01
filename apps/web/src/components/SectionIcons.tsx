import type { ReactNode } from 'react'

export type SectionIconName =
  | 'requirements'
  | 'gaps'
  | 'curriculum'
  | 'roadmap'
  | 'books'
  | 'courses'
  | 'certifications'
  | 'interview'

const paths: Record<SectionIconName, ReactNode> = {
  /** Target / checklist rings */
  requirements: (
    <>
      <circle cx="12" cy="12" r="8" />
      <circle cx="12" cy="12" r="3.5" />
      <path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22" />
    </>
  ),
  /** Progress ring with open gap */
  gaps: (
    <>
      <path d="M19.5 7.5a8 8 0 1 0 1.2 5.8" />
      <path d="M12 8v4l2.5 1.5" />
    </>
  ),
  /** Calendar block */
  curriculum: (
    <>
      <rect x="4" y="5" width="16" height="15" rx="2" />
      <path d="M8 3v4M16 3v4M4 10h16" />
      <path d="M9 14h2M13 14h2M9 17h2" />
    </>
  ),
  /** Path with waypoints */
  roadmap: (
    <>
      <path d="M5 18c3-1 4-5 7-5s4 4 7 5" />
      <circle cx="5" cy="18" r="1.6" />
      <circle cx="12" cy="13" r="1.6" />
      <circle cx="19" cy="18" r="1.6" />
    </>
  ),
  /** Open book */
  books: (
    <>
      <path d="M12 6c-2-1.5-5-2-8-1.5v13c3-.5 6 .2 8 1.5 2-1.3 5-2 8-1.5v-13C17 4 14 4.5 12 6z" />
      <path d="M12 6v13" />
    </>
  ),
  /** Play in circle */
  courses: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M10 8.5v7l6-3.5-6-3.5z" />
    </>
  ),
  /** Badge / shield */
  certifications: (
    <>
      <path d="M12 3l7 3v6c0 4.2-2.8 7.5-7 9-4.2-1.5-7-4.8-7-9V6l7-3z" />
      <path d="M9.5 12l1.8 1.8L15 10" />
    </>
  ),
  /** Speech bubble with ? */
  interview: (
    <>
      <path d="M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H10l-4 3v-3H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z" />
      <path d="M10 9.2c.3-.7 1-.1.1 1.2.4.4.7.7.7 1.3M12 14.5h.01" />
    </>
  ),
}

export function SectionIcon({
  name,
  className = '',
}: {
  name: SectionIconName
  className?: string
}) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
      className={`section-icon ${className}`.trim()}
    >
      <g
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {paths[name]}
      </g>
    </svg>
  )
}
