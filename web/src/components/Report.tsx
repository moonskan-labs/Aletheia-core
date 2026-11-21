import { useMemo, useState } from 'react'
import type { EvidenceResponse, Investigation, InvestigationEvent, InvestigationResult } from '../api/types'
import {
  EvidenceIndexContext,
  EvidenceSelectionContext,
  buildEvidenceIndex,
  defaultSelection,
  revealEvidencePane,
  type EvidenceIndex,
} from '../evidenceIndex'
import { STATUS_LABEL, UNDECIDED_REASON, reason } from '../labels'
import { Citations } from './Cite'
import { AuditTrail } from './AuditTrail'
import { EvidencePane } from './Evidence'
import { Correction, DecisionLabel, Units } from './Findings'
import { ResearchActivity, ResearchInProgress } from './Progress'

interface Props {
  investigation: Investigation
  evidence: EvidenceResponse | null
  events: InvestigationEvent[]
  researchDone: boolean
  finished: boolean
  loadError: string | null
  replay: boolean
  /** The submission returned an existing investigation rather than starting one. */
  reused: boolean
  onRetry: () => void
}

function sourceCount(index: EvidenceIndex): number {
  const ids = [...index.values()].filter((e) => e.evidence.admissible).map((e) => e.evidence.assessment.citation.snapshot_id)
  return new Set(ids).size
}

function RunMeta({ investigation, index, sources, finished, reused }: {
  investigation: Investigation
  index: EvidenceIndex
  sources?: EvidenceResponse['sources']
  finished: boolean
  reused: boolean
}) {
  const seconds = investigation.started_at && investigation.finished_at
    ? Math.round((Date.parse(investigation.finished_at) - Date.parse(investigation.started_at)) / 1000)
    : NaN
  const notes = [
    !finished ? 'Researching' : investigation.status !== 'completed' ? STATUS_LABEL[investigation.status] : null,
    reused && 'Saved result',
    investigation.version > 1 && `Version ${investigation.version}`,
  ].filter(Boolean)
  return (
    <>
      {notes.length > 0 && <p className="meta">{notes.join(' · ')}</p>}
      {finished && (
        <div className="metrics-bar">
          <dl aria-label="Investigation metrics">
            <div><dt>Sources Quoted</dt><dd>{sources === undefined ? '—' : sourceCount(index)}</dd></div>
            <div><dt>Time Taken</dt><dd>{Number.isFinite(seconds) && seconds >= 0 ? `${seconds}s` : '—'}</dd></div>
          </dl>
        </div>
      )}
    </>
  )
}

/**
 * Keeps the decision checkable when the explanation cites nothing, for example a
 * partial result saved with an empty explanation: link the finding's own evidence.
 */
function DecisionEvidence({ result }: { result: InvestigationResult }) {
  const ids = result.finding.evidence_ids
  if (ids.length === 0 || result.explanation.some((unit) => unit.evidence_ids.length > 0)) return null
  return (
    <p>
      {result.explanation.length === 0 ? 'No written explanation was saved. ' : ''}
      The decision rests on this evidence:
      <Citations ids={ids} />
    </p>
  )
}

/** The written answer and its essential caveat or correction, before any detail. */
function Conclusion({ investigation, result }: { investigation: Investigation; result: InvestigationResult }) {
  const summary = [...result.explanation]
  for (const flag of result.finding.qualification_flags) {
    const existing = summary.findIndex(unit => unit.text.trim() === flag.explanation.trim())
    if (existing < 0) {
      summary.push({ text: flag.explanation, evidence_ids: flag.evidence_ids })
    } else {
      const unit = summary[existing]
      summary[existing] = { ...unit, evidence_ids: [...new Set([...unit.evidence_ids, ...flag.evidence_ids])] }
    }
  }
  return (
    <section className="conclusion" aria-labelledby="result-label">
      {investigation.status === 'partial' && (
        <p className="notice-box">
          Partial result: the run stopped before every step finished
          {reason(investigation.stop_reason) ? ` (${reason(investigation.stop_reason)})` : ''}. The decision comes from
          the steps that completed.
        </p>
      )}
      <div className="summary">
        <Units units={summary} />
        <DecisionEvidence result={result} />
      </div>
      {result.almost_correction && <Correction correction={result.almost_correction} />}
    </section>
  )
}

function citedIds(result: InvestigationResult | null): string[] {
  if (!result) return []
  return [
    ...result.explanation.flatMap((u) => u.evidence_ids),
    ...result.finding.qualification_flags.flatMap((f) => f.evidence_ids),
    ...result.finding.evidence_ids,
  ]
}

export function Report(props: Props) {
  const { investigation, evidence, events, researchDone, finished, loadError, replay, reused, onRetry } = props
  const result = finished ? investigation.result : null
  const unconfirmed = result?.outcome === 'unable_to_decide' &&
    (investigation.stop_reason === 'semantic_rejection' || investigation.stop_reason === 'invalid_task_output')
  const runLimitations = result && (!replay || investigation.status === 'partial' || result.outcome === 'unable_to_decide')
    ? [...new Set([...result.limitations, ...result.finding.limitations])]
    : []
  const index = useMemo(() => buildEvidenceIndex(evidence), [evidence])
  const [choice, setChoice] = useState<{ investigation: string; id: string } | null>(null)
  const selected =
    choice?.investigation === investigation.id && index.has(choice.id)
      ? choice.id
      : defaultSelection(index, citedIds(result))
  const selection = useMemo(
    () => ({
      selected,
      select: (id: string, reveal = false) => {
        setChoice({ investigation: investigation.id, id })
        if (reveal) revealEvidencePane()
      },
    }),
    [selected, investigation.id],
  )

  return (
    <EvidenceIndexContext.Provider value={index}>
      <EvidenceSelectionContext.Provider value={selection}>
        <article className="report">
          <header className="report-head">
            <p className="section-label">Claim</p>
            <h1 className="claim">{investigation.claim}</h1>
            {result && (
              <>
                <h2 id="result-label" className="result-label">
                  {unconfirmed ? 'No confirmed decision' : <DecisionLabel decision={result} />}
                  {!unconfirmed && result.finding.qualification_flags.length > 0 && (
                    <span className="result-qualifier">, with a caveat</span>
                  )}
                </h2>
                {!unconfirmed && result.unable_to_decide_reason && (
                  <p className="result-reason">{UNDECIDED_REASON[result.unable_to_decide_reason]}</p>
                )}
              </>
            )}
            <RunMeta
              investigation={investigation}
              index={index}
              sources={evidence?.sources}
              finished={finished}
              reused={reused}
            />
          </header>

          {!researchDone && <ResearchInProgress events={events} replay={replay} />}

          {researchDone && !finished && !loadError && (
            <p className="meta status-line" role="status">
              Research finished. Loading the results…
            </p>
          )}

          {loadError && (
            <section className="outcome" role="alert">
              <h2>Research finished, but the results didn’t load</h2>
              <p className="meta">{loadError}</p>
              <p className="meta">The investigation itself is saved; retrying only fetches it again.</p>
              <button type="button" className="secondary-button" onClick={onRetry}>
                Retry loading results
              </button>
            </section>
          )}

          {finished && investigation.clarification_questions && (
            <section className="outcome">
              <h2>Needs clarification before researching</h2>
              <ul>
                {investigation.clarification_questions.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </section>
          )}

          {finished && investigation.method_limitation && (
            <section className="outcome">
              <h2 id="result-label">This claim needs a different research method</h2>
              <p>{investigation.method_limitation.explanation}</p>
            </section>
          )}

          {finished && investigation.error && (
            <section className="outcome" role="alert">
              <h2 id="result-label">No decision</h2>
              <p>{investigation.error.message}</p>
              <p className="meta">A failed investigation is not evidence that the claim is false.</p>
            </section>
          )}

          {(result || (finished && events.length > 0)) && (
            <div className="report-body">
              <div className="report-main">
                {result && (
                  <>
                    {unconfirmed ? (
                      <section className="conclusion" aria-labelledby="result-label">
                        <p>The final check did not confirm a decision. The collected sources are listed under Evidence below.</p>
                        <p className="meta">This does not establish that evidence is insufficient or conflicting.</p>
                      </section>
                    ) : (
                      <Conclusion investigation={investigation} result={result} />
                    )}
                    {runLimitations.length > 0 && (
                      <section className="notice-box" aria-label="Investigation limitations">
                        <ul className="limitations">{runLimitations.map(note => <li key={note}>{note}</li>)}</ul>
                      </section>
                    )}
                    <EvidencePane sources={evidence?.sources ?? []} explanation={result.explanation.map((u) => u.text)} />
                  </>
                )}

                <AuditTrail key={investigation.id} sources={evidence?.sources} index={index}>
                  <ResearchActivity events={events} />
                </AuditTrail>

              </div>
            </div>
          )}
        </article>
      </EvidenceSelectionContext.Provider>
    </EvidenceIndexContext.Provider>
  )
}
