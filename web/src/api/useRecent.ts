import { useEffect, useState } from 'react'
import type { DataSource } from './source'
import type { Investigation } from './types'

/**
 * The newest saved investigations, fetched each time the home page shows (`active`).
 * Sources without a recent list, and backends that can't answer, give an empty list:
 * the home page then simply has no recent section.
 */
export function useRecent(source: DataSource, active: boolean): Investigation[] {
  const [recent, setRecent] = useState<Investigation[]>([])
  useEffect(() => {
    if (!active || !source.recent) return
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
  }, [source, active])
  return recent
}
