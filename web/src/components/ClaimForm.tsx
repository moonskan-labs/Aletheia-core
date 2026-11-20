import { useId, useState, type FormEvent } from 'react'
import { Icon } from './Icon'

const MAX_CLAIM_LENGTH = 500

interface Props {
  onSubmit: (claim: string) => void
  /** A submission is in flight: keep the text, block resubmission. */
  submitting: boolean
  /** Investigation isn't available here (replay-only page). */
  unavailableReason?: string
  /** Offered while unavailable when checking the backend again could help. */
  onRetry?: () => void
}

/** Layout C's search box: one line, a search icon, and Verify. */
export function ClaimForm({ onSubmit, submitting, unavailableReason, onRetry }: Props) {
  const [claim, setClaim] = useState('')
  const noteId = useId()
  const trimmed = claim.trim()
  const unavailable = Boolean(unavailableReason)

  function handle(event: FormEvent) {
    event.preventDefault()
    if (trimmed && !submitting && !unavailable) onSubmit(trimmed)
  }

  return (
    <form className="claim-form" onSubmit={handle} aria-busy={submitting}>
      <label htmlFor="claim" className="sr-only">
        Claim to check
      </label>
      <div className="search-box">
        <Icon name="search" size={22} />
        <input
          id="claim"
          value={claim}
          maxLength={MAX_CLAIM_LENGTH}
          disabled={unavailable}
          aria-describedby={unavailable ? noteId : undefined}
          placeholder="Enter a claim to verify"
          autoComplete="off"
          onChange={(e) => setClaim(e.target.value)}
        />
        <button type="submit" className="verify" disabled={unavailable || submitting || !trimmed}>
          {submitting ? 'Verifying…' : 'Verify'}
          <Icon name="enter" size={16} />
        </button>
      </div>
      {unavailable && (
        <p id={noteId} className="meta claim-form-note">
          {unavailableReason}
          {onRetry && (
            <>
              {' '}
              <button type="button" className="link-button" onClick={onRetry}>
                Retry connection
              </button>
            </>
          )}
        </p>
      )}
    </form>
  )
}
