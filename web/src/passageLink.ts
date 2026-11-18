/**
 * A link that opens a source at the quoted passage, using a URL text fragment
 * (`#:~:text=`). Browsers that support it scroll to the passage and highlight it;
 * the rest open the page as usual. Returns null when the quotation cannot be matched
 * on a rendered page, so the caller links to the page alone.
 */

/** Markdown and table marks from page extraction never appear in the rendered page. */
const UNMATCHABLE = /[|*#`[\]<>_~\\]/
const EDGE_WORDS = 5

/** A dash, comma or ampersand is fragment syntax, so each must be percent-encoded. */
function encode(text: string): string {
  return encodeURIComponent(text).replaceAll('-', '%2D')
}

export function passageLink(url: string, quote: string): string | null {
  const words = quote.trim().split(/\s+/).filter(Boolean)
  if (words.length < 3 || UNMATCHABLE.test(quote)) return null
  let page: URL
  try {
    page = new URL(url)
  } catch {
    return null
  }
  if (page.protocol !== 'http:' && page.protocol !== 'https:') return null
  // A long quotation is matched by its first and last words: line breaks and
  // punctuation in the middle then cannot stop the match.
  const text =
    words.length <= EDGE_WORDS * 2
      ? encode(words.join(' '))
      : `${encode(words.slice(0, EDGE_WORDS).join(' '))},${encode(words.slice(-EDGE_WORDS).join(' '))}`
  page.hash = ''
  return `${page.href.replace(/#$/, '')}#:~:text=${text}`
}
