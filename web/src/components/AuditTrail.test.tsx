// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { buildEvidenceIndex } from '../evidenceIndex'
import { RECORDINGS } from '../fixtures'
import { AuditTrail } from './AuditTrail'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

it('brings the trail into view when a panel opens, and not when it closes', () => {
  const scroll = vi.fn()
  Element.prototype.scrollIntoView = scroll
  const recording = RECORDINGS.find((r) => !r.sample)!
  render(
    <AuditTrail sources={recording.evidence.sources} index={buildEvidenceIndex(recording.evidence)}>
      <p>log</p>
    </AuditTrail>,
  )
  expect(scroll).not.toHaveBeenCalled()

  fireEvent.click(screen.getByRole('button', { name: 'Research log' }))
  expect(scroll).toHaveBeenCalledTimes(1)
  expect(scroll.mock.contexts[0]).toBe(screen.getByRole('region', { name: 'Investigation Audit Trail' }))
  expect(scroll.mock.calls[0][0]).toMatchObject({ block: 'start' })

  fireEvent.click(screen.getByRole('button', { name: 'Research log' }))
  expect(scroll).toHaveBeenCalledTimes(1)
})
