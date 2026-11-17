import type { EvidenceResponse, Investigation, InvestigationEvent } from '../api/types'
import apollo from './live/apollo-11-landing-date.json'
import venus from './live/venus-closest-planet.json'
import { sampleMisleadingComparison } from './sample-misleading-comparison'

/** An exported investigation the client can replay without a backend. */
export interface Recording {
  label: string
  /** True for invented development data; the UI says so on screen. */
  sample: boolean
  investigation: Investigation
  evidence: EvidenceResponse
  events: InvestigationEvent[]
}

type Captured = Pick<Recording, 'investigation' | 'evidence' | 'events'>

/**
 * Real runs of the search-and-verdict loop against Token Factory and Tavily, saved on
 * 2026-11-16 and unedited. The quotations are the pages' own text at the time.
 */
function recorded(label: string, captured: unknown): Recording {
  return { label, sample: false, ...(captured as Captured) }
}

export const RECORDINGS: Recording[] = [
  recorded('A date on the record: true', apollo),
  recorded('A wrong fact: false', venus),
  sampleMisleadingComparison,
]
