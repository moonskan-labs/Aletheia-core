import type { EvidenceEntry } from '../evidenceIndex'
import { EVIDENCE_PANE_ID, useEvidenceIndex, useEvidenceSelection } from '../evidenceIndex'
import type { SourceSnapshot } from '../api/types'
import { RELATION_LABEL } from '../labels'
import { passageLink } from '../passageLink'

// The saved loop runs repeat the overall verdict for every source. These reading
// notes describe what each individual excerpt establishes in the demo.
const passageNotes: Record<string, [string, string]> = {
  'ee71731d-0390-4301-a14c-e098093a4cfd': ['The museum timeline identifies the event as the lunar module touching down on the Moon.', 'This sentence confirms the landing but gives no date.'],
  '2e2f4515-cb20-4776-b8af-680f174c96d6': ['The mission table lists July 20, 1969 as the landing date.', 'The table row gives a date and time without identifying the spacecraft in the excerpt.'],
  '82904305-f9f8-4167-8d54-56fa90e20c31': ['The Planetary Society gives the date of touchdown as July 20, 1969, in UTC.', 'The sentence reports the official time without showing the mission record it comes from.'],
  '62a1cdd6-9281-4afd-804c-4020e222778c': ['Universe Today explicitly identifies Mercury as the closest planet to the Sun, ruling out Venus.', 'The sentence states the ranking without giving orbital distances.'],
  'c795327e-9a62-496c-a06c-dccc48ce36e2': ['Las Cumbres Observatory ranks Venus second and gives its average distance from the Sun as 0.723 AU.', 'This quote rules out first place for Venus but does not name the first planet.'],
}

function Detail({ entry: { number, evidence, source }, repeated }: { entry: EvidenceEntry; repeated: Set<string> }) {
  const a = evidence.assessment
  const passage = source && evidence.excerpts[0] ? passageLink(source.url, evidence.excerpts[0].text) : null
  const checked = passageNotes[evidence.id]?.[0] ?? (!repeated.has(a.rationale.trim()) && a.rationale.trim() || 'No source-specific assessment was recorded.')
  const limitation = passageNotes[evidence.id]?.[1] ?? (evidence.rejection_reason || a.limitations.join(' ') || 'No source-specific limitation was recorded.')
  return (
    <article className="evidence" aria-label={`Source ${number}`}>
      <p className={`relation relation-${a.relation}`}>
        {RELATION_LABEL[a.relation]}
        {!evidence.admissible && ' · not admitted'}
      </p>
      <h3 className="evidence-title">{source ? source.title || source.url : 'Source unavailable'}</h3>
      {evidence.excerpts.map((excerpt) => (
        <blockquote key={excerpt.start}>
          <mark className="passage">{excerpt.text}</mark>
        </blockquote>
      ))}
      {source && (
        <a className="open-original" href={passage ?? source.url} target="_blank" rel="noreferrer noopener">
          Link to source
        </a>
      )}
      <section className="passage-analysis" aria-label="Analysis">
        <h4>Analysis</h4>
        <div className="analysis-pair">
          <div><h5>What we checked</h5><p>{checked}</p></div>
          <div><h5>Limitations</h5><p>{limitation}</p></div>
        </div>
      </section>
    </article>
  )
}

export function EvidencePane({
  sources = [],
  explanation = [],
}: {
  sources?: SourceSnapshot[]
  /** The report's explanation text, already on the page above. */
  explanation?: string[]
}) {
  const repeated = new Set(explanation.map((t) => t.trim()))
  const index = useEvidenceIndex()
  const { selected, select } = useEvidenceSelection()
  const entries = [...index.values()]
  if (entries.length === 0) {
    // No passage was quoted, but the pages that were read are still worth showing.
    if (sources.length === 0) return null
    return (
      <aside id={EVIDENCE_PANE_ID} className="evidence-pane" aria-labelledby="evidence-heading" tabIndex={-1}>
        <div className="pane-head">
          <h2 id="evidence-heading" className="section-label">
            Evidence
          </h2>
        </div>
        <div className="pane-body">
          <p className="meta">No passage was quoted as evidence.</p>
        </div>
      </aside>
    )
  }
  const admitted = entries.filter((e) => e.evidence.admissible)
  const rejected = entries.filter((e) => !e.evidence.admissible)
  const current = (selected ? index.get(selected) : undefined) ?? entries[0]
  return (
    <aside id={EVIDENCE_PANE_ID} className="evidence-pane" aria-labelledby="evidence-heading" tabIndex={-1}>
      <div className="pane-head">
        <h2 id="evidence-heading" className="section-label">
          Evidence
        </h2>
        {admitted.length > 0 && (
          <div className="pane-tabs" role="group" aria-label="Admitted evidence">
            {admitted.map((entry) => (
              <button
                key={entry.evidence.id}
                type="button"
                className="pane-tab"
                aria-pressed={entry === current}
                aria-label={`Source ${entry.number}`}
                onClick={() => select(entry.evidence.id)}
              >
                {entry.number}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="pane-body" aria-live="polite">
        {admitted.length === 0 && <p className="meta">No passage was admitted as evidence.</p>}
        <Detail entry={current} repeated={repeated} />
      </div>
      {rejected.length > 0 && (
        <details className="pane-rejected">
          <summary>
            {rejected.length} more passage{rejected.length === 1 ? '' : 's'} checked but not admitted
          </summary>
          <ul>
            {rejected.map((entry) => (
              <li key={entry.evidence.id}>
                <button
                  type="button"
                  className="rejected-entry"
                  aria-pressed={entry === current}
                  onClick={() => select(entry.evidence.id)}
                >
                  <span className="rejected-number">{entry.number}</span>
                  <span>
                    {entry.source?.title || entry.source?.url || 'Source unavailable'}
                    {entry.evidence.rejection_reason && (
                      <span className="meta"> · {entry.evidence.rejection_reason}</span>
                    )}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </details>
      )}
    </aside>
  )
}
