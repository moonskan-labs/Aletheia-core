import type { EvidenceEntry } from '../evidenceIndex'
import { EVIDENCE_PANE_ID, useEvidenceIndex, useEvidenceSelection } from '../evidenceIndex'
import type { SourceSnapshot } from '../api/types'
import { RELATION_LABEL, formatTime } from '../labels'
import { passageLink } from '../passageLink'

/** One piece of evidence: relation, source, the exact excerpt, why it counts, the link. */
function Detail({ entry: { number, evidence, source }, repeated }: { entry: EvidenceEntry; repeated: Set<string> }) {
  const a = evidence.assessment
  const passage = source && evidence.excerpts[0] ? passageLink(source.url, evidence.excerpts[0].text) : null
  return (
    <article className="evidence" aria-label={`Source ${number}`}>
      <p className={`relation relation-${a.relation}`}>
        {RELATION_LABEL[a.relation]}
        {!evidence.admissible && ' · not admitted'}
      </p>
      <h3 className="evidence-title">{source ? source.title || source.url : 'Source unavailable'}</h3>
      {a.publisher && <p className="evidence-meta">{a.publisher}</p>}
      {source?.published_date && <p className="evidence-meta">Published {source.published_date}</p>}
      {evidence.excerpts.map((excerpt) => (
        <blockquote key={excerpt.start}>
          <mark className="passage">{excerpt.text}</mark>
        </blockquote>
      ))}
      {!evidence.admissible && evidence.rejection_reason && (
        <p>
          <span className="inline-label">Not admitted</span>
          {evidence.rejection_reason}
        </p>
      )}
      {/* The simple loop gives every quotation the explanation as its rationale; don't repeat it. */}
      {!repeated.has(a.rationale.trim()) && (
        <p>
          <span className="inline-label">Why it counts</span>
          {a.rationale}
        </p>
      )}
      {a.limitations.length > 0 && <p className="meta">Limitations: {a.limitations.join(' ')}</p>}
      {source && (
        <a className="open-original" href={passage ?? source.url} target="_blank" rel="noreferrer noopener">
          {passage ? 'Open the original at this passage' : 'Open the original'}
        </a>
      )}
      <details className="trace">
        <summary>Citation details</summary>
        <dl>
          <dt>Spans</dt>
          <dd>{evidence.excerpts.map((e) => e.span_ids.join(', ')).join(' | ')}</dd>
          <dt>Snapshot</dt>
          <dd>{a.citation.snapshot_id}</dd>
          <dt>Evidence ID</dt>
          <dd>{evidence.id}</dd>
          {a.origin && (
            <>
              <dt>Origin</dt>
              <dd>{a.origin}</dd>
            </>
          )}
          <dt>Independence</dt>
          <dd>{a.independence}</dd>
          {source && (
            <>
              <dt>Retrieved</dt>
              <dd>{formatTime(source.retrieved_at)}</dd>
              <dt>URL</dt>
              <dd>{source.url}</dd>
              <dt>Content hash</dt>
              <dd>{source.content_hash}</dd>
            </>
          )}
        </dl>
      </details>
    </article>
  )
}

/**
 * The evidence pane: one entry at a time, numbered as cited, below what was checked.
 * Passages checked but not admitted sit collapsed.
 */
function host(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

/** Every page the run read, quoted or not, so the reader can see what was consulted. */
function PagesRead({ sources, quoted }: { sources: SourceSnapshot[]; quoted: Set<string> }) {
  if (sources.length === 0) return null
  return (
    <details className="pane-rejected pane-sources">
      <summary>
        {sources.length} page{sources.length === 1 ? '' : 's'} read
      </summary>
      <ul>
        {sources.map((source) => (
          <li key={source.id}>
            <a href={source.url} target="_blank" rel="noreferrer noopener">
              {source.title || source.url}
            </a>
            <span className="meta">
              {' '}
              · {host(source.url)}
              {quoted.has(source.id) ? ' · quoted' : ''}
            </span>
          </li>
        ))}
      </ul>
    </details>
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
  const quoted = new Set(entries.map((e) => e.evidence.assessment.citation.snapshot_id))
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
        <PagesRead sources={sources} quoted={quoted} />
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
      <PagesRead sources={sources} quoted={quoted} />
    </aside>
  )
}
