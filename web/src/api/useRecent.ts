import { useEffect, useState } from 'react'
import type { DataSource } from './source'
import type { Investigation } from './types'
import type { BackendStatus } from './useBackendStatus'

/** The backend answered: listing works whether or not research is enabled. */
function reachable(status: BackendStatus): boolean {
  return status === 'ready' || status === 'research_disabled'
}

/**
 * The newest saved investigations, fetched each time the home page shows (`active`)
 * and each time the backend becomes reachable, so a backend that starts after the
 * page loaded (and is found by "Retry connection") brings its history with it.
 * Sources without a recent list, and backends that can't answer, give an empty list:
 * the home page then simply has no recent section.
 */
export function useRecent(source: DataSource, active: boolean, status: BackendStatus): Investigation[] {
  const [recent, setRecent] = useState<Investigation[]>([])
  const listable = reachable(status)
  useEffect(() => {
    if (!active || !listable || !source.recent) return
    const controller = new AbortController()
    source.recent(controller.signal).then(
      (list) => {
        if (!controller.signal.aborted) setRecent(list)
      },
      () => {
        if (!controller.signal.aborted) setRecent([])
      },
    )
    return () => controller.abort()
  }, [source, active, listable])
  return recent
}
