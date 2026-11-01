const KEY = 'jobify.sections.v1'

type CollapseMap = Record<string, boolean>

function read(): CollapseMap {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw) as CollapseMap
    return parsed && typeof parsed === 'object' ? parsed : {}
  } catch {
    return {}
  }
}

function write(map: CollapseMap) {
  try {
    localStorage.setItem(KEY, JSON.stringify(map))
  } catch {
    // ignore quota / private mode
  }
}

/** Open state for a section. Default: collapsed (false). */
export function isSectionOpen(id: string): boolean {
  const map = read()
  return map[id] === true
}

export function setSectionOpen(id: string, open: boolean): void {
  const map = read()
  map[id] = open
  write(map)
}
