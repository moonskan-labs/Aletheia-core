| Run | True/false answers | Right among those | Total matches | 95% interval | Tokens (trusted subset) | Quote downgrades |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 20261115-baseline-qwen235 | 66/77 | 56/66 | 62/77 | 70–88% | 717180 + unknown for 1 claims | 2 |
| 20261116-baseline-qwen235-b | 67/77 | 58/67 | 64/77 | 73–90% | 729173 | 3 |
| 20261116-baseline-qwen235-c | 65/77 | 55/65 | 61/77 | 69–87% | 724525 + unknown for 1 claims | 2 |
| 20261116-fix2-estimates-a | 64/77 | 54/64 | 60/77 | 67–86% | 726215 + unknown for 1 claims | 5 |
| 20261116-fix2-estimates-b | 65/77 | 56/65 | 61/77 | 69–87% | 705475 + unknown for 3 claims | 3 |
| 20261116-fix2-estimates-c | 67/77 | 58/67 | 64/77 | 73–90% | 739621 | 3 |

No result is 'no answer', never cannot_settle. Total matches include cannot_settle. Intervals use the existing Wilson 95% function; they do not measure run-to-run noise.
Tokens cover only the included trusted claims; excluded historical claims are ignored. Missing usage is reported as unknown rather than zero.

Wrong answers — 20261115-baseline-qwen235: a-01 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), t-12 (cannot_settle; expected true), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), f-20 (cannot_settle; expected false), g-08 (false; expected true), u-08 (false; expected cannot_settle), a-19 (true; expected false)
No answer: g-04
Wrong answers — 20261116-baseline-qwen235-b: t-02 (cannot_settle; expected true), c-04 (cannot_settle; expected false), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), t-21 (cannot_settle; expected true), g-08 (false; expected true), u-08 (false; expected cannot_settle)
No answer: none
Wrong answers — 20261116-baseline-qwen235-c: a-01 (cannot_settle; expected false), f-04 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), t-12 (cannot_settle; expected true), f-11 (cannot_settle; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), g-08 (false; expected true), u-08 (false; expected cannot_settle)
No answer: f-22
Wrong answers — 20261116-fix2-estimates-a: a-01 (cannot_settle; expected false), t-05 (cannot_settle; expected true), f-04 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), t-21 (cannot_settle; expected true), f-20 (cannot_settle; expected false), u-08 (false; expected cannot_settle), a-19 (true; expected false)
No answer: g-04
Wrong answers — 20261116-fix2-estimates-b: g-01 (cannot_settle; expected true), t-05 (cannot_settle; expected true), f-04 (cannot_settle; expected false), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), u-08 (false; expected cannot_settle)
No answer: g-04, f-25, u-10
Wrong answers — 20261116-fix2-estimates-c: t-02 (cannot_settle; expected true), a-01 (cannot_settle; expected false), t-05 (cannot_settle; expected true), c-04 (true; expected false), a-06 (true; expected false), c-06 (true; expected false), a-09 (true; expected false), c-12 (true; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), c-15 (false; expected true), u-08 (false; expected cannot_settle)
No answer: none

Pairwise differences (including cannot_settle and no answer):
- 20261115-baseline-qwen235 / 20261116-baseline-qwen235-b: 9/77 answers differ; total-match gap 2/77.
- 20261115-baseline-qwen235 / 20261116-baseline-qwen235-c: 7/77 answers differ; total-match gap 1/77.
- 20261115-baseline-qwen235 / 20261116-fix2-estimates-a: 6/77 answers differ; total-match gap 2/77.
- 20261115-baseline-qwen235 / 20261116-fix2-estimates-b: 11/77 answers differ; total-match gap 1/77.
- 20261115-baseline-qwen235 / 20261116-fix2-estimates-c: 8/77 answers differ; total-match gap 2/77.
- 20261116-baseline-qwen235-b / 20261116-baseline-qwen235-c: 8/77 answers differ; total-match gap 3/77.
- 20261116-baseline-qwen235-b / 20261116-fix2-estimates-a: 9/77 answers differ; total-match gap 4/77.
- 20261116-baseline-qwen235-b / 20261116-fix2-estimates-b: 10/77 answers differ; total-match gap 3/77.
- 20261116-baseline-qwen235-b / 20261116-fix2-estimates-c: 5/77 answers differ; total-match gap 0/77.
- 20261116-baseline-qwen235-c / 20261116-fix2-estimates-a: 9/77 answers differ; total-match gap 1/77.
- 20261116-baseline-qwen235-c / 20261116-fix2-estimates-b: 10/77 answers differ; total-match gap 0/77.
- 20261116-baseline-qwen235-c / 20261116-fix2-estimates-c: 7/77 answers differ; total-match gap 3/77.
- 20261116-fix2-estimates-a / 20261116-fix2-estimates-b: 7/77 answers differ; total-match gap 1/77.
- 20261116-fix2-estimates-a / 20261116-fix2-estimates-c: 6/77 answers differ; total-match gap 4/77.
- 20261116-fix2-estimates-b / 20261116-fix2-estimates-c: 7/77 answers differ; total-match gap 3/77.
