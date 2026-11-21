import { useEffect, useId, useRef, useState, type ReactNode } from 'react'
import type { SourceSnapshot } from '../api/types'
import type { EvidenceIndex } from '../evidenceIndex'
import { PagesRead } from './PagesRead'

export function AuditTrail({ sources, index, children }: {
  sources?: SourceSnapshot[]
  index: EvidenceIndex
  children: ReactNode
}) {
  const id = useId()
  const [active, setActive] = useState<string | null>(null)
  const section = useRef<HTMLElement>(null)
  // An opened panel starts below the fold: bring the trail up so the click shows something.
  useEffect(() => {
    if (!active) return
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    section.current?.scrollIntoView?.({ block: 'start', behavior: reduce ? 'auto' : 'smooth' })
  }, [active])
  const views = [
    { name: 'Pages Read', label: `Pages Read ${sources?.length ?? '—'}`, heading: `All ${sources?.length ?? 0} pages reviewed`, content: <PagesRead sources={sources} index={index} /> },
    { name: 'Research log', label: 'Research log', heading: 'Research log', content: children },
  ]
  return (
    <section ref={section} className="audit-trail" aria-label="Investigation Audit Trail">
      <div className="audit-row">
        <strong>Investigation Audit Trail</strong>
        <div className="audit-actions">
          {views.map((view, i) => (
            <button key={view.name} type="button" id={`${id}-button-${i}`}
              aria-controls={`${id}-panel-${i}`} aria-expanded={active === view.name}
              onClick={() => setActive(active === view.name ? null : view.name)}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d={i === 0 ? 'M14 2H5v20h14V8l-5-6v6h5' : 'm4 5 7 7-7 7m9 0h7'} />
              </svg>{view.label}<span aria-hidden="true">⌄</span>
            </button>
          ))}
        </div>
      </div>
      {views.map((view, i) => (
        <div key={view.name} id={`${id}-panel-${i}`} className="audit-panel" hidden={active !== view.name}
          role="region" aria-labelledby={`${id}-button-${i}`}>
          <header><strong>{view.heading}</strong>
            <button onClick={() => { setActive(null); document.getElementById(`${id}-button-${i}`)?.focus() }}>Close ×</button>
          </header>
          {view.content}
        </div>
      ))}
    </section>
  )
}
