import type {
  EvidenceRelation,
  FlagDimension,
  FlagType,
  InvestigationEvent,
  InvestigationStatus,
  Stage,
  UndecidedReason,
  Verdict,
} from './api/types'

export const VERDICT_LABEL: Record<Verdict, string> = {
  true: 'True',
  false: 'False',
  almost: 'Almost',
}

/** The visible result label for each undecided reason (docs/research-pipeline.md). */
export const UNDECIDED_LABEL: Record<UndecidedReason, string> = {
  insufficient_evidence: 'Insufficient evidence',
  conflicting_evidence: 'Conflicting evidence',
}

/** Only for a malformed decision with no reason; the contract never produces one. */
export const UNDECIDED_FALLBACK = 'Unable to decide'

export const UNDECIDED_REASON: Record<UndecidedReason, string> = {
  insufficient_evidence: 'There wasn’t enough admissible evidence to decide either way.',
  conflicting_evidence: 'Admissible sources disagree, and the evidence doesn’t settle which is right.',
}

const STAGE_LABEL: Record<Stage, string> = {
  interpreting: 'Interpreting the claim',
  planning: 'Planning searches',
  searching: 'Searching',
  extracting: 'Reading sources',
  verifying: 'Checking evidence',
  synthesizing: 'Writing the answer',
  comparing: 'Comparing with the earlier version',
}

/** Machine reasons from the backend, in plain words. Unknown codes pass through. */
const REASON_LABEL: Record<string, string> = {
  evidence_sufficient: 'enough evidence',
  no_useful_query: 'no useful searches left',
  budget_exhausted: 'research budget used up',
  deadline_exceeded: 'time limit reached',
  provider_failure: 'a provider failed',
  storage_failure: 'storage failed',
  interrupted: 'interrupted',
  unsupported_method: 'this claim needs a different research method',
  invalid_task_output: 'a research answer could not be validated',
  semantic_rejection: 'the final check did not confirm a decision',
  empty_content: 'no readable text',
  followup_round_limit: 'follow-up limit reached',
  verdict_with_quotes: 'a verdict backed by quotations',
  no_new_pages: 'no new pages to read',
  duplicate_content: 'same content as a page already read',
  extraction_failed: 'the page could not be read',
  rate_limited: 'rate limited',
  timeout: 'timed out',
}

export function reason(code: string | null): string | null {
  return code ? (REASON_LABEL[code] ?? code.replaceAll('_', ' ')) : null
}

export const FLAG_LABEL: Record<FlagType, string> = {
  misleading_comparison: 'Misleading comparison',
  narrow_scope: 'Narrower than claimed',
}

export const DIMENSION_LABEL: Record<FlagDimension, string> = {
  population: 'population',
  timeframe: 'timeframe',
  units: 'units',
  baseline: 'baseline',
  condition: 'conditions',
  jurisdiction: 'jurisdiction',
  definition: 'definition',
  evaluation_setup: 'evaluation setup',
  benchmark_subset: 'benchmark subset',
}

export const RELATION_LABEL: Record<EvidenceRelation, string> = {
  supports: 'Supports the claim',
  contradicts: 'Contradicts the claim',
  context: 'Context',
  irrelevant: 'Not relevant',
}

export const STATUS_LABEL: Record<InvestigationStatus, string> = {
  queued: 'Queued',
  running: 'Researching',
  needs_clarification: 'Needs clarification',
  completed: 'Completed',
  partial: 'Partial result',
  failed: 'Failed',
}

function text(value: string | undefined): string | null {
  return value ? value : null
}

const PROVIDER_LABEL: Record<string, string> = { nebius: 'Token Factory', tavily: 'Tavily' }
const OPERATION_LABEL: Record<string, string> = { model: 'model call', search: 'search', extract: 'page read' }

/** "Tavily search" or "Token Factory model call"; null when the event does not say. */
function providerCall(p: Record<string, string>): string | null {
  const provider = PROVIDER_LABEL[p.provider ?? '']
  const operation = OPERATION_LABEL[p.operation ?? '']
  return provider && operation ? `${provider} ${operation}` : null
}

/** Counts for the research log's summary line, from the run's own events. */
export function runCounts(events: InvestigationEvent[]): { searches: number; pages: number; modelCalls: number } {
  const modelCalls = new Set(
    events
      .filter((e) => e.type === 'provider_attempt_started' && e.payload.provider === 'nebius')
      .map((e) => e.payload.provider_call_id),
  )
  return {
    searches: events.filter((e) => e.type === 'search_completed').length,
    pages: events.filter((e) => e.type === 'source_extracted' && e.payload.duplicate !== 'true').length,
    modelCalls: modelCalls.size,
  }
}

/** One plain line per event. Shows what actually happened; never a percentage. */
export function describeEvent(event: InvestigationEvent): string {
  const p = event.payload
  switch (event.type) {
    case 'route_revised':
      return 'Revised the research approach'
    case 'model_attempt_finished':
      return 'Finished a reasoning attempt'
    case 'task_finished':
      return 'Finished a research step'
    case 'task_started':
      return 'Started a research step'
    case 'run_configured':
      return 'Set the research limits'
    case 'clarification_decision':
      return 'Checked whether the claim needs clarification'
    case 'research_stopped':
      return 'Stopped collecting evidence'
    case 'provider_attempt_started':
      return providerCall(p) ? `Started a ${providerCall(p)}` : 'Started a provider request'
    case 'provider_attempt_finished': {
      const failed = text(p.outcome) && p.outcome !== 'success' ? `: ${reason(p.outcome)}` : ''
      return `${providerCall(p) ? `Finished a ${providerCall(p)}` : 'Finished a provider request'}${failed}`
    }
    case 'provider_call_rejected':
      return 'A provider request could not start'
    case 'provider_retry_stopped':
      return 'Stopped retrying a provider request'
    case 'provider_retry_scheduled':
      return 'Scheduled another provider attempt'
    case 'pipeline_failed':
      return 'Research could not finish'
    case 'source_selected':
      return 'Selected a source to read'
    case 'assessment_rejected':
      return 'A passage assessment did not pass validation'
    case 'search_incomplete':
      return 'Some planned searches did not finish'
    case 'investigation_queued':
      return 'Queued'
    case 'investigation_started':
      return 'Started research'
    case 'stage_started':
      return STAGE_LABEL[p.stage as Stage] ?? 'Started the next step'
    case 'claim_interpreted':
      return 'Scoped the claim to one checkable assertion'
    case 'clarification_required':
      return 'Needs clarification before researching'
    case 'route_selected':
      return `Chose ${p.route === 'deep' ? 'deeper research' : 'a quick check'}${text(p.reason) ? `: ${p.reason}` : ''}`
    case 'search_started':
      return `Searching “${text(p.query) ?? '…'}”`
    case 'search_completed':
      return `Search “${text(p.query) ?? '…'}” returned ${text(p.result_count) ?? '?'} results`
    case 'source_extracted':
      return `Read ${text(p.url) ?? 'a source'}${p.duplicate === 'true' ? ' (duplicate of a page already read)' : ''}`
    case 'source_rejected':
      return `Couldn’t use ${text(p.url) ?? 'a source'}${reason(text(p.reason)) ? `: ${reason(text(p.reason))}` : ''}`
    case 'sources_deferred':
      return text(p.reason)?.startsWith('Social')
        ? `Skipped ${text(p.count) ?? 'some'} search results from social and video sites`
        : `Left ${text(p.count) ?? 'some'} search results unread to stay within page limits`
    case 'research_gate':
      return p.action === 'followup'
        ? `Decided to search further${text(p.gap) ? `: ${p.gap}` : ''}`
        : `Decided to stop searching${reason(text(p.reason)) ? `: ${reason(text(p.reason))}` : ''}`
    case 'evidence_checked': {
      const relation = RELATION_LABEL[p.relation as EvidenceRelation]
      const verdict = p.admissible === 'true' ? 'admitted' : 'not admitted'
      return `Checked a passage: ${verdict}${relation ? ` (${relation.toLowerCase()})` : ''}`
    }
    case 'route_escalated':
      return `Escalated to deeper research${text(p.reason) ? `: ${p.reason}` : ''}`
    case 'followup_planned':
      return `Planned a follow-up search${text(p.gap) ? ` for: ${p.gap}` : ''}`
    case 'budget_reached':
      return `Stopped researching: ${reason(text(p.reason)) ?? 'limit reached'}`
    case 'task_output_rejected':
      if (p.reason === 'quotations_point_the_other_way')
        return 'Withdrew a verdict: its own quotations pointed the other way'
      if (p.task === 'check') return 'The second check of the quotations could not be run'
      if (p.task === 'plan') return 'Search planning failed; searched for the claim text instead'
      return `Rejected a malformed model answer${text(p.task) ? ` (${(p.task ?? '').replaceAll('_', ' ')})` : ''}`
    case 'qualification_flag_dropped':
      return 'Dropped a qualification flag that didn’t pass validation'
    case 'comparison_completed':
      return 'Compared with the earlier version'
    case 'consistency_flagged':
      return 'Flagged an inconsistency with the earlier version'
    case 'investigation_completed':
      return 'Finished'
    case 'investigation_partial':
      return 'Finished with a partial result'
    case 'investigation_failed':
      return 'Failed before reaching a decision'
  }
}

export function formatTime(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

/** A calendar date as YYYY-MM-DD in the reader's time zone, for the mono run line. */
export function formatDate(iso: string | null): string | null {
  if (!iso) return null
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

/** Time since the run's first step, as mm:ss, for the research log. */
export function elapsed(iso: string, start: string): string {
  const seconds = Math.max(0, Math.round((Date.parse(iso) - Date.parse(start)) / 1000))
  return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`
}
