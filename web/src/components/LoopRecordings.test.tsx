// @vitest-environment jsdom
import { cleanup, fireEvent, render, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import type { InvestigationEvent } from '../api/types'
import { RECORDINGS, type Recording } from '../fixtures'
import { describeEvent, runCounts } from '../labels'
import { passageLink } from '../passageLink'
import { Report } from './Report'

/** Real runs of the search-and-verdict loop, saved unedited (src/fixtures/live). */
const live = RECORDINGS.filter((r) => !r.sample)

function show(recording: Recording): HTMLElement {
  const { investigation, evidence, events } = recording
  return render(
    <Report
      investigation={investigation}
      evidence={evidence}
      events={events}
      researchDone
      finished
      loadError={null}
      replay
      reused={false}
      onRetry={() => {}}
    />,
  ).container
}

function event(type: InvestigationEvent['type'], payload: Record<string, string>): InvestigationEvent {
  return { investigation_id: 'i', sequence: 1, timestamp: '2026-11-16T00:00:00Z', type, stage: null, payload }
}

afterEach(cleanup)

describe('passageLink', () => {
  const page = 'https://example.org/a/b?x=1#old'

  it('quotes a short passage whole and replaces any existing fragment', () => {
    expect(passageLink(page, 'Mercury is the closest planet')).toBe(
      'https://example.org/a/b?x=1#:~:text=Mercury%20is%20the%20closest%20planet',
    )
  })

  it('matches a long passage by its first and last five words', () => {
    const quote = 'one two three four five six seven eight nine ten eleven twelve'
    expect(passageLink(page, quote)).toBe(
      'https://example.org/a/b?x=1#:~:text=one%20two%20three%20four%20five,eight%20nine%20ten%20eleven%20twelve',
    )
  })

  it('encodes the characters that are fragment syntax', () => {
    expect(passageLink(page, 'a well-known fact, said A&B')).toContain('well%2Dknown%20fact%2C%20said%20A%26B')
  })

  it('gives no passage link when the page could not match the quotation', () => {
    expect(passageLink(page, 'Landing date | July 20, 1969')).toBeNull() // a table row
    expect(passageLink(page, 'The module *Eagle* landed')).toBeNull() // markdown emphasis
    expect(passageLink(page, 'too short')).toBeNull()
    expect(passageLink('javascript:alert(1)', 'three plain words')).toBeNull()
    expect(passageLink('not a url', 'three plain words')).toBeNull()
  })
})

describe('recorded loop runs', () => {
  it('has a true and a false run, neither marked as invented', () => {
    expect(live.map((r) => r.investigation.result?.verdict)).toEqual(['true', 'false'])
  })

  it.each(live)('$label: shows the verdict, its quotations and every page read', (recording) => {
    const page = show(recording)
    const verdict = recording.investigation.result!.verdict === 'true' ? 'True' : 'False'
    expect(within(page).getByRole('heading', { level: 2, name: verdict })).toBeTruthy()
    const pane = within(page).getByRole('complementary')
    // The excerpt on screen is the saved page's own text.
    const first = recording.evidence.evidence[0]
    expect(pane.querySelector('blockquote')?.textContent).toBe(first.excerpts[0].text)
    const read = within(pane).getByText(`${recording.evidence.sources.length} pages read`)
    const links = [...read.closest('details')!.querySelectorAll('a')].map((a) => a.getAttribute('href'))
    expect(links).toEqual(recording.evidence.sources.map((s) => s.url))
    expect(read.closest('details')!.textContent).toContain('quoted')
  })

  it.each(live)('$label: every quotation links to its own source, at the passage where possible', (recording) => {
    const page = show(recording)
    const pane = within(page).getByRole('complementary')
    const sources = new Map(recording.evidence.sources.map((s) => [s.id, s]))
    for (const [i, item] of recording.evidence.evidence.entries()) {
      fireEvent.click(within(pane).getByRole('button', { name: `Source ${i + 1}` }))
      const source = sources.get(item.assessment.citation.snapshot_id)!
      const expected = passageLink(source.url, item.excerpts[0].text)
      const link = within(pane).getByRole('link', { name: /^Open the original/ })
      expect(link.getAttribute('href')).toBe(expected ?? source.url)
      expect(link.textContent).toBe(expected ? 'Open the original at this passage' : 'Open the original')
    }
  })

  it.each(live)('$label: the research log names the searches, pages and model calls', (recording) => {
    const page = show(recording)
    const counts = runCounts(recording.events)
    expect(counts).toEqual({ searches: 3, pages: recording.evidence.sources.length, modelCalls: 3 })
    const summary = page.querySelector('details.activity summary')!.textContent
    expect(summary).toContain('3 searches')
    expect(summary).toContain(`${counts.pages} pages read`)
    expect(summary).toContain('3 model calls')
    const lines = recording.events.map(describeEvent)
    expect(lines).toContain('Started a Token Factory model call')
    expect(lines).toContain('Finished a Tavily search')
    expect(lines).toContain('Finished a Tavily page read')
    expect(lines).toContain('Decided to stop searching: a verdict backed by quotations')
    // No machine code reaches the reader; page addresses may contain underscores.
    expect(lines.every((line) => !line.replace(/https?:\S+/g, '').includes('_'))).toBe(true)
  })
})

describe('loop events in plain words', () => {
  it('describes each loop-specific step', () => {
    expect(describeEvent(event('sources_deferred', { count: '2', reason: 'Social and video sites are not read.' }))).toBe(
      'Skipped 2 search results from social and video sites',
    )
    expect(describeEvent(event('sources_deferred', { count: '2', reason: 'Per-round page limit.' }))).toBe(
      'Left 2 search results unread to stay within page limits',
    )
    expect(
      describeEvent(event('task_output_rejected', { task: 'verdict', reason: 'quotations_point_the_other_way' })),
    ).toBe('Withdrew a verdict: its own quotations pointed the other way')
    expect(describeEvent(event('task_output_rejected', { task: 'plan', reason: 'invalid_response' }))).toBe(
      'Search planning failed; searched for the claim text instead',
    )
    expect(describeEvent(event('research_gate', { action: 'stop', reason: 'no_new_pages' }))).toBe(
      'Decided to stop searching: no new pages to read',
    )
    expect(
      describeEvent(event('provider_attempt_finished', { provider: 'tavily', operation: 'extract', outcome: 'timeout' })),
    ).toBe('Finished a Tavily page read: timed out')
    // An older recording without provider details keeps the general wording.
    expect(describeEvent(event('provider_attempt_started', {}))).toBe('Started a provider request')
  })
})

describe('a run that quoted nothing', () => {
  it('still lists the pages that were read', () => {
    const recording = live[0]
    const result = recording.investigation.result!
    const unsettled = {
      outcome: 'unable_to_decide' as const,
      verdict: null,
      unable_to_decide_reason: 'insufficient_evidence' as const,
      almost_correction: null,
    }
    const page = show({
      ...recording,
      investigation: {
        ...recording.investigation,
        stop_reason: 'budget_exhausted',
        result: {
          ...result,
          ...unsettled,
          explanation: [],
          limitations: ['Not settled: the pages do not state the date.'],
          finding: { ...result.finding, ...unsettled, evidence_ids: [], limitations: [] },
        },
      },
      evidence: { sources: recording.evidence.sources, evidence: [] },
    })
    expect(within(page).getByRole('heading', { level: 2, name: 'Insufficient evidence' })).toBeTruthy()
    const pane = within(page).getByRole('complementary')
    expect(pane.textContent).toContain('No passage was quoted as evidence.')
    expect(within(pane).getByText(`${recording.evidence.sources.length} pages read`)).toBeTruthy()
    expect(page.textContent).toContain('Not settled: the pages do not state the date.')
  })
})

describe('what a loop result says it checked', () => {
  const venus = live.find((r) => r.investigation.claim.startsWith('Venus'))!

  it('lists the searches it ran and the pages it read, as bullets', () => {
    const container = show(venus)
    const checked = within(container.querySelector('[aria-labelledby="findings-heading"]') as HTMLElement)
    const items = checked.getAllByRole('listitem').map((li) => li.textContent)
    expect(items[0]).toContain('Searched the web for: “average orbital distance of Venus from the Sun”')
    expect(items[1]).toBe('Read 6 pages; each one is listed under Evidence below.')
    // The claim is checked as submitted; the headline already shows it.
    expect(items).toHaveLength(2)
  })

  it('leaves out the staged pipeline’s scope note and route name', () => {
    const container = show(venus)
    expect(container.textContent).not.toContain('Comparisons and scope were not assessed')
    const facts = container.querySelector('.run-meta p')!.textContent
    // The date is shown in local time, so it differs by time zone.
    expect(facts).toMatch(/^2 quoted · 6 pages read · 15 s · 2026-11-1[67]$/)
  })
})

describe('the evidence pane under a loop result', () => {
  it('does not repeat the explanation as each quotation’s rationale', () => {
    const apollo = live.find((r) => r.investigation.claim.startsWith('The Apollo'))!
    const container = show(apollo)
    const pane = container.querySelector('.evidence-pane') as HTMLElement
    expect(pane.textContent).not.toContain('Why it counts')
    expect(pane.textContent).toContain('The lunar module touched down on the surface on the Moon.')
  })
})
