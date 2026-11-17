| Run | True/false answers | Right among those | Total matches | 95% interval | Tokens (trusted subset) | Quote downgrades |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 20261116-simple-gptoss120-a | 59/77 | 53/59 | 59/77 | 66–85% | 809970 | 0 |
| 20261116-simple-filter-gptoss120-a | 53/77 | 50/53 | 56/77 | 62–81% | 763309 | 0 |
| 20261116-simple-check-gptoss120-a | 50/77 | 48/50 | 55/77 | 61–80% | 814753 | 0 |

No result is 'no answer', never cannot_settle. Total matches include cannot_settle. Intervals use the existing Wilson 95% function; they do not measure run-to-run noise.
Tokens cover only the included trusted claims; excluded historical claims are ignored. Missing usage is reported as unknown rather than zero.

Wrong answers — 20261116-simple-gptoss120-a: t-02 (cannot_settle; expected true), f-01 (cannot_settle; expected false), c-01 (cannot_settle; expected true), g-01 (cannot_settle; expected true), t-05 (cannot_settle; expected true), a-06 (true; expected false), t-12 (false; expected true), f-11 (cannot_settle; expected false), g-04 (cannot_settle; expected true), c-12 (cannot_settle; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), g-05 (cannot_settle; expected true), f-20 (cannot_settle; expected false), u-08 (false; expected cannot_settle), a-16 (true; expected false), t-24 (cannot_settle; expected true)
No answer: none
Wrong answers — 20261116-simple-filter-gptoss120-a: t-02 (cannot_settle; expected true), c-01 (cannot_settle; expected true), g-01 (cannot_settle; expected true), t-05 (cannot_settle; expected true), a-06 (true; expected false), a-07 (cannot_settle; expected false), t-12 (cannot_settle; expected true), f-11 (cannot_settle; expected false), g-04 (cannot_settle; expected true), c-12 (cannot_settle; expected false), x-01 (cannot_settle; expected true), x-04 (cannot_settle; expected true), x-08 (false; expected true), g-07 (cannot_settle; expected true), t-21 (cannot_settle; expected true), f-20 (cannot_settle; expected false), c-18 (cannot_settle; expected false), u-08 (false; expected cannot_settle), f-22 (cannot_settle; expected false), a-18 (cannot_settle; expected false), t-24 (cannot_settle; expected true)
No answer: none
Wrong answers — 20261116-simple-check-gptoss120-a: t-02 (cannot_settle; expected true), a-01 (cannot_settle; expected false), c-01 (cannot_settle; expected true), g-01 (cannot_settle; expected true), t-05 (cannot_settle; expected true), f-07 (cannot_settle; expected false), a-06 (true; expected false), t-12 (cannot_settle; expected true), f-11 (cannot_settle; expected false), g-04 (cannot_settle; expected true), c-12 (cannot_settle; expected false), x-01 (false; expected true), x-04 (cannot_settle; expected true), x-08 (cannot_settle; expected true), t-15 (cannot_settle; expected true), a-13 (cannot_settle; expected false), g-07 (cannot_settle; expected true), t-21 (cannot_settle; expected true), f-19 (cannot_settle; expected false), f-20 (cannot_settle; expected false), a-16 (cannot_settle; expected false), t-24 (cannot_settle; expected true)
No answer: none

Pairwise differences (including cannot_settle and no answer):
- 20261116-simple-gptoss120-a / 20261116-simple-filter-gptoss120-a: 11/77 answers differ; total-match gap 3/77.
- 20261116-simple-gptoss120-a / 20261116-simple-check-gptoss120-a: 13/77 answers differ; total-match gap 4/77.
- 20261116-simple-filter-gptoss120-a / 20261116-simple-check-gptoss120-a: 13/77 answers differ; total-match gap 1/77.
