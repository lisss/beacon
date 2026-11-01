type LogoProps = {
  className?: string
  title?: string
  onClick?: () => void
}

/** Path-J + gap-bridge mark only (for reuse next to links, etc.). */
export function PathJMark({ className = '' }: { className?: string }) {
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
 * Path-J + gap-bridge mark with wordmark.
 * Color via currentColor (shared with wordmark).
 */
export function Logo({ className = '', title = 'Jobify', onClick }: LogoProps) {
  const inner = (
    <>
      <PathJMark className="logo-mark" />
      <span className="logo-wordmark">{title}</span>
    </>
  )

  if (onClick) {
    return (
      <button
        type="button"
        className={`logo ${className}`.trim()}
        aria-label={title}
        onClick={onClick}
      >
        {inner}
      </button>
    )
  }

  return (
    <span className={`logo ${className}`.trim()} aria-label={title}>
      {inner}
    </span>
  )
}
