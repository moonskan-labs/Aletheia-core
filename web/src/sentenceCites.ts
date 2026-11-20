/**
 * Places a unit's citation numbers after the sentence each quotation supports, as in
 * Skanda's layout. The backend attaches every citation to the whole explanation unit,
 * so the sentence is chosen by wording: each quotation goes after the sentence that
 * shares the most distinctive words and figures with it (the earliest one on a tie).
 * Every citation is still shown exactly once, and a one-sentence unit is unchanged.
 */

const STOP = new Set(
  (
    'that this with from have were which their there about than they them then also into been only does more ' +
    'most such what when where while these those page pages claim saved supplied provided state states stated ' +
    'explicitly directly'
  ).split(' '),
)

function words(text: string): Set<string> {
  const found = text.toLowerCase().match(/[a-z][a-z'’-]{3,}|\d[\d,.]*/g) ?? []
  return new Set(found.filter((w) => !STOP.has(w)))
}

/** Sentence boundaries: end punctuation, a space, then a capital (so "U.S. democracy" stays whole). */
export function sentences(text: string): string[] {
  return text.split(/(?<=[.!?])\s+(?=[A-Z])/)
}

export interface CitedSentence {
  text: string
  ids: string[]
}

export function citeSentences(text: string, ids: string[], quoted: (id: string) => string): CitedSentence[] {
  const parts = sentences(text)
  if (parts.length < 2 || ids.length < 2) return [{ text, ids }]
  const vocab = parts.map(words)
  const placed: CitedSentence[] = parts.map((s) => ({ text: s, ids: [] }))
  for (const id of ids) {
    const quote = words(quoted(id))
    const scores = vocab.map((v) => [...v].filter((w) => quote.has(w)).length)
    placed[scores.indexOf(Math.max(...scores))].ids.push(id)
  }
  return placed
}
