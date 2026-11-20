import { describe, expect, it } from 'vitest'
import { citeSentences } from './sentenceCites'

const quotes: Record<string, string> = {
  a: 'India is the world’s largest democracy with a population of more than 1.4 billion people.',
  b: 'India is the largest democracy in the world, whereas the United States is the oldest.',
  c: 'Using this index, the U.S. is categorized as a “flawed democracy” in 2025.',
  d: 'Expert ratings of U.S. democracy placed the country closer to an illiberal democracy.',
}
const quoted = (id: string) => quotes[id]

describe('citation numbers after the sentence they support', () => {
  it('splits a two-sentence explanation by which quotation each sentence uses', () => {
    const text =
      'The pages identify India as the world’s largest democracy and the United States as the oldest. ' +
      'They also rate U.S. democracy as flawed and closer to an illiberal democracy.'
    const parts = citeSentences(text, ['a', 'b', 'c', 'd'], quoted)
    expect(parts.map((p) => p.ids)).toEqual([
      ['a', 'b'],
      ['c', 'd'],
    ])
    expect(parts.map((p) => p.text).join(' ')).toBe(text)
  })

  it('keeps one sentence, or one citation, as it was', () => {
    expect(citeSentences('India is the largest democracy.', ['a', 'b'], quoted)).toEqual([
      { text: 'India is the largest democracy.', ids: ['a', 'b'] },
    ])
    const two = 'India is large. It votes.'
    expect(citeSentences(two, ['a'], quoted)).toEqual([{ text: two, ids: ['a'] }])
  })

  it('puts a quotation that matches nothing after the first sentence, never dropping it', () => {
    const parts = citeSentences('RNA is single-stranded. No page contradicts this.', ['x', 'y'], () => 'unrelated')
    expect(parts.map((p) => p.ids)).toEqual([['x', 'y'], []])
  })

  it('does not split inside an abbreviation such as U.S.', () => {
    const parts = citeSentences('Ratings of U.S. democracy are low. India is largest.', ['c', 'a'], quoted)
    expect(parts).toHaveLength(2)
    expect(parts[0].ids).toEqual(['c'])
  })
})
