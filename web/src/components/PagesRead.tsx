import type { SourceSnapshot } from '../api/types'
import type { EvidenceIndex } from '../evidenceIndex'

function host(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

export function PagesRead({ sources, index }: { sources?: SourceSnapshot[]; index: EvidenceIndex }) {
  if (!sources?.length) return <p>No pages recorded.</p>
  const quoted = new Set<string>()
  const publishers = new Map<string, string>()
  for (const { evidence } of index.values()) {
    const { citation, publisher } = evidence.assessment
    if (publisher) publishers.set(citation.snapshot_id, publisher)
    if (evidence.admissible) quoted.add(citation.snapshot_id)
  }

  return (
    <ol className="audit-pages">
      {sources.map(source => (
        <li key={source.id}>
          <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title || source.url}</a>
          <div>{[
            publishers.get(source.id),
            host(source.url),
            source.published_date && `Published ${source.published_date}`,
            quoted.has(source.id) ? 'Quoted in verdict' : 'Reviewed',
          ].filter(Boolean).join(' · ')}</div>
        </li>
      ))}
    </ol>
  )
}
