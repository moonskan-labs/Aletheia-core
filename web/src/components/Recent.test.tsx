// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { liveSource, replaySource, type DataSource } from '../api/source'
import type { Investigation } from '../api/types'
import { canRecheck, unavailableReason, useBackendStatus } from '../api/useBackendStatus'
import { useRecent } from '../api/useRecent'
import { RECORDINGS } from '../fixtures'
import { Home } from './Home'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

const decided = RECORDINGS.find((r) => r.investigation.result)!.investigation
const running: Investigation = { ...decided, id: 'running-1', claim: 'Still being checked.', status: 'running', result: null }
const healthy = (research_enabled: boolean) => ({ status: 'ok', database: 'ok', research_enabled })

// Wired as App wires it: the backend status gates the recent list.
function Harness({ source, onOpen = () => {} }: { source: DataSource; onOpen?: (id: string) => void }) {
  const backend = useBackendStatus(source)
  const recent = useRecent(source, true, backend.status)
  return (
    <Home
      unavailableReason={unavailableReason(backend.status)}
      onRetryBackend={canRecheck(backend.status) ? backend.recheck : undefined}
      submitting={false}
      error={null}
      recordings={[]}
      recent={recent}
      onSubmit={() => {}}
      onOpen={onOpen}
    />
  )
}

describe('recent investigations on the home page', () => {
  it('loads saved history once a backend that was down is found by Retry connection', async () => {
    const health = vi.fn().mockRejectedValueOnce(new Error('down')).mockResolvedValue(healthy(true))
    const recent = vi.fn().mockResolvedValue([decided])
    render(<Harness source={{ ...liveSource, health, recent }} />)
    await act(async () => {})
    expect(screen.queryByRole('heading', { name: 'Recent investigations' })).toBeNull()
    expect(recent).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: 'Retry connection' }))
    await act(async () => {})

    expect(screen.getByRole('heading', { name: 'Recent investigations' })).toBeTruthy()
    expect(screen.getByText(decided.claim)).toBeTruthy()
  })

  it('shows saved history when the backend answers with research turned off', async () => {
    const health = vi.fn().mockResolvedValue(healthy(false))
    const recent = vi.fn().mockResolvedValue([decided])
    render(<Harness source={{ ...liveSource, health, recent }} />)
    await act(async () => {})
    expect(screen.getByText(decided.claim)).toBeTruthy()
  })

  it('lists past investigations with their decision or status, and opens one', async () => {
    const onOpen = vi.fn()
    const recent = vi.fn().mockResolvedValue([running, decided])
    const health = vi.fn().mockResolvedValue(healthy(true))
    render(<Harness source={{ ...liveSource, health, recent }} onOpen={onOpen} />)
    await act(async () => {})

    expect(screen.getByRole('heading', { name: 'Recent investigations' })).toBeTruthy()
    const rows = screen.getAllByRole('button').filter((b) => b.classList.contains('sample'))
    expect(rows).toHaveLength(2)
    expect(rows[0].textContent).toContain('Still being checked.')
    expect(rows[0].textContent).toContain('Researching')
    expect(rows[1].textContent).toContain(decided.claim)

    fireEvent.click(rows[1])
    expect(onOpen).toHaveBeenCalledWith(decided.id)
  })

  it('shows no recent section when the backend cannot list investigations', async () => {
    const recent = vi.fn().mockRejectedValue(new Error('That investigation wasn’t found.'))
    const health = vi.fn().mockResolvedValue(healthy(true))
    render(<Harness source={{ ...liveSource, health, recent }} />)
    await act(async () => {})
    expect(screen.queryByRole('heading', { name: 'Recent investigations' })).toBeNull()
  })

  it('never asks a backend for past investigations in replay mode', async () => {
    const fetch = vi.fn()
    vi.stubGlobal('fetch', fetch)
    render(<Harness source={replaySource} />)
    await act(async () => {})
    expect(fetch).not.toHaveBeenCalled()
    expect(screen.queryByRole('heading', { name: 'Recent investigations' })).toBeNull()
  })

  it('asks the live backend for the newest ten', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ investigations: [decided] })))
    vi.stubGlobal('fetch', fetch)
    expect(await liveSource.recent!()).toEqual([decided])
    expect(fetch.mock.calls[0][0]).toBe('/api/investigations?limit=10')
  })
})
