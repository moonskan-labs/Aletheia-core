| Run | True/false answers | Right among those | Total matches | 95% interval | Tokens (trusted subset) | Quote downgrades |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 20261115-baseline-qwen235 | 66/77 | 56/66 | 62/77 | 70–88% | 717180 + unknown for 1 claims | 2 |
| 20261116-baseline-qwen235-b | 67/77 | 58/67 | 64/77 | 73–90% | 729173 | 3 |
| 20261116-baseline-qwen235-c | 65/77 | 55/65 | 61/77 | 69–87% | 724525 + unknown for 1 claims | 2 |
| 20261116-fix1-comparisons-a | 61/77 | 52/61 | 58/77 | 65–84% | 772636 | 1 |
| 20261116-fix1-comparisons-b | 56/77 | 48/56 | 54/77 | 59–79% | 761295 + unknown for 1 claims | 1 |
| 20261116-fix1-comparisons-c | 59/77 | 50/59 | 56/77 | 62–81% | 771876 | 1 |

No result is 'no answer', never cannot_settle. Total matches include cannot_settle. Intervals use the existing Wilson 95% function; they do not measure run-to-run noise.
Tokens cover only the included trusted claims; excluded historical claims are ignored. Missing usage is reported as unknown rather than zero.

Wrong answers — 20261115-baseline-qwen235: a-01 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), t-12 (cannot_settle; expected true), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), f-20 (cannot_settle; expected false), g-08 (false; expected true), u-08 (false; expected cannot_settle), a-19 (true; expected false)
No answer: g-04
Wrong answers — 20261116-baseline-qwen235-b: t-02 (cannot_settle; expected true), c-04 (cannot_settle; expected false), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), t-21 (cannot_settle; expected true), g-08 (false; expected true), u-08 (false; expected cannot_settle)
No answer: none
Wrong answers — 20261116-baseline-qwen235-c: a-01 (cannot_settle; expected false), f-04 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), t-12 (cannot_settle; expected true), f-11 (cannot_settle; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), g-08 (false; expected true), u-08 (false; expected cannot_settle)
No answer: f-22
Wrong answers — 20261116-fix1-comparisons-a: c-01 (cannot_settle; expected true), f-04 (cannot_settle; expected false), c-04 (cannot_settle; expected false), t-08 (cannot_settle; expected true), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-02 (cannot_settle; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-13 (cannot_settle; expected true), a-12 (true; expected false), c-18 (cannot_settle; expected false), u-08 (false; expected cannot_settle), t-23 (cannot_settle; expected true), c-19 (cannot_settle; expected true), t-24 (false; expected true)
No answer: none
Wrong answers — 20261116-fix1-comparisons-b: c-01 (cannot_settle; expected true), f-04 (cannot_settle; expected false), c-04 (true; expected false), t-08 (cannot_settle; expected true), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-09 (true; expected false), c-12 (cannot_settle; expected false), x-01 (false; expected true), x-02 (cannot_settle; expected true), x-04 (cannot_settle; expected true), x-07 (cannot_settle; expected true), x-08 (false; expected true), c-13 (cannot_settle; expected true), a-12 (cannot_settle; expected false), c-18 (cannot_settle; expected false), u-08 (false; expected cannot_settle), t-23 (cannot_settle; expected true), c-19 (cannot_settle; expected true), t-24 (cannot_settle; expected true), f-23 (cannot_settle; expected false)
No answer: g-04
Wrong answers — 20261116-fix1-comparisons-c: c-01 (cannot_settle; expected true), f-04 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), t-12 (cannot_settle; expected true), a-09 (true; expected false), c-12 (cannot_settle; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-13 (cannot_settle; expected true), t-17 (cannot_settle; expected true), a-12 (true; expected false), c-16 (true; expected false), c-18 (cannot_settle; expected false), u-08 (false; expected cannot_settle), t-23 (cannot_settle; expected true), c-19 (cannot_settle; expected true), t-24 (cannot_settle; expected true), f-23 (cannot_settle; expected false)
No answer: none

Pairwise differences (including cannot_settle and no answer):
- 20261115-baseline-qwen235 / 20261116-baseline-qwen235-b: 9/77 answers differ; total-match gap 2/77.
- 20261115-baseline-qwen235 / 20261116-baseline-qwen235-c: 7/77 answers differ; total-match gap 1/77.
- 20261115-baseline-qwen235 / 20261116-fix1-comparisons-a: 19/77 answers differ; total-match gap 4/77.
- 20261115-baseline-qwen235 / 20261116-fix1-comparisons-b: 21/77 answers differ; total-match gap 8/77.
- 20261115-baseline-qwen235 / 20261116-fix1-comparisons-c: 19/77 answers differ; total-match gap 6/77.
- 20261116-baseline-qwen235-b / 20261116-baseline-qwen235-c: 8/77 answers differ; total-match gap 3/77.
- 20261116-baseline-qwen235-b / 20261116-fix1-comparisons-a: 14/77 answers differ; total-match gap 6/77.
- 20261116-baseline-qwen235-b / 20261116-fix1-comparisons-b: 20/77 answers differ; total-match gap 10/77.
- 20261116-baseline-qwen235-b / 20261116-fix1-comparisons-c: 18/77 answers differ; total-match gap 8/77.
- 20261116-baseline-qwen235-c / 20261116-fix1-comparisons-a: 16/77 answers differ; total-match gap 3/77.
- 20261116-baseline-qwen235-c / 20261116-fix1-comparisons-b: 20/77 answers differ; total-match gap 7/77.
- 20261116-baseline-qwen235-c / 20261116-fix1-comparisons-c: 16/77 answers differ; total-match gap 5/77.
- 20261116-fix1-comparisons-a / 20261116-fix1-comparisons-b: 8/77 answers differ; total-match gap 4/77.
- 20261116-fix1-comparisons-a / 20261116-fix1-comparisons-c: 9/77 answers differ; total-match gap 2/77.
- 20261116-fix1-comparisons-b / 20261116-fix1-comparisons-c: 9/77 answers differ; total-match gap 2/77.
