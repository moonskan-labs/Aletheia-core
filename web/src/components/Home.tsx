import type { Investigation } from '../api/types'
import type { Recording } from '../fixtures'
import { FLAG_LABEL, STATUS_LABEL } from '../labels'
import { ClaimForm } from './ClaimForm'
import { DecisionLabel } from './Findings'

/** Layout C's pill: the sample claim and its decision. */
function SamplePill({ recording, onOpen }: { recording: Recording; onOpen: () => void }) {
  const result = recording.investigation.result
  const flags = [...new Set(result?.finding.qualification_flags.map((x) => x.type) ?? [])]
  return (
    <li>
      <button type="button" className="sample-pill" onClick={onOpen}>
        <span>{recording.investigation.claim}</span>
        <span className="meta">
          {result && <DecisionLabel decision={result} />}
          {flags.map((f) => ` · ${FLAG_LABEL[f]}`).join('')}
          {recording.sample && ' · invented sample'}
        </span>
      </button>
    </li>
  )
}

const WHEN = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' })

/** A past investigation from this backend: its decision, or its status while it has none. */
function RecentRow({ investigation, onOpen }: { investigation: Investigation; onOpen: () => void }) {
  const { result } = investigation
  return (
    <li>
      <button type="button" className="sample" onClick={onOpen}>
        <span className="sample-claim">{investigation.claim}</span>
        <span className="meta">
          {result ? <DecisionLabel decision={result} /> : STATUS_LABEL[investigation.status]}
          {` · ${WHEN.format(new Date(investigation.created_at))}`}
        </span>
        <span className="sample-open" aria-hidden="true">
          →
        </span>
      </button>
    </li>
  )
}

interface Props {
  /** Why claims can't be submitted right now; undefined when they can. */
  unavailableReason?: string
  onRetryBackend?: () => void
  submitting: boolean
  error: string | null
  recordings: Recording[]
  /** Past investigations from the live backend, newest first. */
  recent?: Investigation[]
  onSubmit: (claim: string) => void
  onOpen: (id: string) => void
}

export function Home({ unavailableReason, onRetryBackend, submitting, error, recordings, recent = [], onSubmit, onOpen }: Props) {
  return (
    <section className="home">
      <div className="hero">
        <h1>
          Verify any claim against <em>live web sources</em>
        </h1>
        <ClaimForm
          onSubmit={onSubmit}
          submitting={submitting}
          unavailableReason={unavailableReason}
          onRetry={onRetryBackend}
        />
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        {recordings.length > 0 && (
          <details className="examples compact-details" data-fit="samples">
            <summary>Try a sample claim</summary>
            <ul className="pills">
              {recordings.map((r) => (
                <SamplePill key={r.investigation.id} recording={r} onOpen={() => onOpen(r.investigation.id)} />
              ))}
            </ul>
          </details>
        )}
      </div>

      {recent.length > 0 && (
        <details className="recent compact-details">
          <summary><h2>Recent investigations</h2></summary>
          <ul className="samples">
            {recent.map((i) => (
              <RecentRow key={i.id} investigation={i} onOpen={() => onOpen(i.id)} />
            ))}
          </ul>
        </details>
      )}
    </section>
  )
}
