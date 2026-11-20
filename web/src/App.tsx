import { useLayoutEffect } from 'react'
import { nebiusLogo, tavilyLogo, tavilyDarkLogo } from './providerLogos'
import { dataSource } from './api/source'
import { canRecheck, unavailableReason, useBackendStatus } from './api/useBackendStatus'
import { useInvestigation } from './api/useInvestigation'
import { useRecent } from './api/useRecent'
import { Home } from './components/Home'
import { Icon } from './components/Icon'
import { Report } from './components/Report'

const replay = dataSource.kind === 'replay'

export default function App() {
  const { state, open, submit, retryLoad, close } = useInvestigation(dataSource)
  const backend = useBackendStatus(dataSource)
  const recent = useRecent(dataSource, !state.investigation && !state.submitting, backend.status)
  const { investigation, evidence, events, submitting, researchDone, finished, loadError, error, reused } = state
  const recording = dataSource.recordings.find((r) => r.investigation.id === investigation?.id)
  const live = backend.status === 'ready'

  // Refit automatic disclosures on navigation or resize. Manual disclosure clicks
  // are intentionally allowed to grow the document.
  useLayoutEffect(() => {
    function fitOverview() {
      const root = document.documentElement
      for (const panel of document.querySelectorAll<HTMLDetailsElement>('details[data-fit]')) {
        panel.open = window.innerHeight >= 560 && (panel.dataset.fit !== 'samples' || window.innerWidth >= 620)
        if (root.scrollHeight > root.clientHeight + 1) panel.open = false
      }
    }
    fitOverview()
    window.addEventListener('resize', fitOverview)
    return () => window.removeEventListener('resize', fitOverview)
  }, [investigation, finished, recent?.length, error])

  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <button type="button" className="wordmark" onClick={close} aria-label="Aletheia home">
            <Icon name="fingerprint" size={28} />
            <span>ALETHEIA</span>
          </button>
          <p className={`mode${live ? ' live' : ''}`} role="status">
            <Icon name="globe" size={15} />
            {replay ? (
              <span>
                Sample mode
                <span className="mode-detail">{recording?.sample ? ' · invented sample data' : ' · recorded investigations'}</span>
              </span>
            ) : live ? (
              'Live research'
            ) : (
              'Research offline'
            )}
          </p>
        </div>
      </header>

      <main>
        {investigation ? (
          <>
            <button type="button" className="back" onClick={close}>
              ← {replay ? 'All sample investigations' : 'Check another claim'}
            </button>
            <Report
              investigation={investigation}
              evidence={evidence}
              events={events}
              researchDone={researchDone}
              finished={finished}
              loadError={loadError}
              replay={replay}
              reused={reused}
              onRetry={retryLoad}
              onReplay={replay ? () => void open(investigation.id, { animate: true }) : undefined}
            />
            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
          </>
        ) : (
          <Home
            unavailableReason={unavailableReason(backend.status)}
            onRetryBackend={canRecheck(backend.status) ? backend.recheck : undefined}
            submitting={submitting}
            error={error}
            recordings={dataSource.recordings}
            recent={recent}
            onSubmit={(claim) => void submit(claim, {})}
            onOpen={(id) => void open(id)}
          />
        )}
      </main>
      <footer className="provider-footer">
        <span className="provider-label">Powered by</span>
        <div className="provider-logos">
          <a href="https://nebius.com/services/token-factory">
            <img src={nebiusLogo} alt="Nebius" height="20" />
            <span>Token Factory</span>
          </a>
          <a href="https://www.tavily.com">
            <picture>
              <source media="(prefers-color-scheme: dark)" srcSet={tavilyDarkLogo} />
              <img src={tavilyLogo} alt="Tavily" height="21" />
            </picture>
          </a>
        </div>
      </footer>
    </>
  )
}
