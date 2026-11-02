import { Link } from 'react-router-dom'

type LogoProps = {
  className?: string
  title?: string
  onClick?: () => void
  /** Use an h1 for the homepage brand (SEO). */
  asHeading?: boolean
}

/** Casty mark (gap bridge) mark only (for reuse next to links, etc.). */
export function CastyMark({ className = '' }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 40 40"
      fill="none"
      aria-hidden
      className={className}
    >
      <g
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M14 20h5V16h5V12h5V8" />
        <path d="M6 30h7" />
        <path d="M27 30h7" />
        <path d="M13 30c0-3.8 3.2-6.2 7-6.2s7 2.4 7 6.2" />
      </g>
    </svg>
  )
}

/**
 * Casty mark (gap bridge) mark with wordmark.
 * Color via currentColor (shared with wordmark).
 */
export function Logo({
  className = '',
  title = 'Casty',
  onClick,
  asHeading = false,
}: LogoProps) {
  const inner = (
    <>
      <CastyMark className="logo-mark" />
      <span className="logo-wordmark">{title}</span>
    </>
  )

  const classNames = `logo ${className}`.trim()

  if (onClick) {
    return (
      <button
        type="button"
        className={classNames}
        aria-label={title}
        onClick={onClick}
      >
        {inner}
      </button>
    )
  }

  const link = (
    <Link to="/" className={classNames} aria-label={title}>
      {inner}
    </Link>
  )

  if (asHeading) {
    return <h1 className="logo-heading">{link}</h1>
  }

  return link
}
