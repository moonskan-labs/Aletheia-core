# Labeling the v1 backend-eval claims

For Chandra and Pari. Label **blind**: don't look at each other's files, or at anything under
`evals/drafts/`, until both of you have pushed your labels.

## What to write per claim (40 claims, table below)

**1. The label**, at `evals/labels/<your-name>/<id>.json`, in the format and decision rules in
[../README.md](../README.md) ("Choosing the decision"). `status: "draft"`, `labelers: ["<your-name>"]`,
`split: "tuning"`, and `id`, `claim`, `context`, `case_type` copied unchanged from the table.
Check it with `python evals/validate.py`.

**2. The stage keys**, at `evals/stage-keys/<your-name>/<id>.json`. These let the grader check whether
the backend found and used the evidence that settles the claim. One entry per `key_sources` item, same order:

```json
{
  "id": "b0001",
  "expected_route": "research",
  "key_sources": [
    {
      "urls": ["<the page you used>", "<its PDF or mirror, if any>"],
      "sites": ["<host whose every page counts, e.g. unfccc.int; [] if only the exact page counts>"],
      "decisive_quotes": ["<one or two sentences copied exactly from the page>"],
      "expected_relation": "supports | contradicts | context"
    }
  ]
}
```

- `decisive_quotes`: copy and paste from the page; don't retype. Short is fine: the sentence that settles the claim.
- `sites`: use the host for official publishers (`nasa.gov`, `bls.gov`); use `[]` for a single article on a big general site.
- `expected_route` is fixed by the table: `decline` rows should end as "can't check this kind of claim". Label them anyway.

## The 40 claims

| id | case_type | route | claim |
|---|---|---|---|
| b0001 | direct_fact | research | The Apollo 11 lunar module landed on the Moon on 20 July 1969. |
| b0002 | direct_fact | research | Venus is the closest planet to the Sun. |
| b0003 | direct_fact | research | The James Webb Space Telescope, launched in November 2021, observes the universe primarily in infrared light. |
| b0004 | insufficient | research | Microbial life exists beneath the present-day ice shell of Europa. |
| b0005 | conflict | research | The Younger Dryas cooling event was triggered by an extraterrestrial impact approximately 12,800 years ago. |
| b0006 | direct_fact | research | Antibiotics do not treat infections caused solely by viruses. |
| b0007 | direct_fact | research | The measles, mumps and rubella vaccine has been shown to cause autism. |
| b0008 | direct_fact | research | Smallpox, declared eradicated by the World Health Assembly in 1979, is caused by variola virus. |
| b0009 | insufficient | research | Daily oral resveratrol supplementation extends lifespan in healthy adult humans. |
| b0010 | conflict | research | Annual mammography screening starting at age 40 reduces all-cause mortality in average-risk women compared with no screening. |
| b0011 | direct_fact | research | The SHA-256 cryptographic hash algorithm produces a 256-bit digest. |
| b0012 | direct_fact | research | The original version of the Python programming language was first publicly released in 2001. |
| b0013 | direct_fact | research | The World Wide Web software, released by CERN into the public domain in May 1993, enabled royalty-free reuse. |
| b0014 | insufficient | research | GPT-4 was trained with exactly 1.76 trillion parameters. |
| b0015 | conflict | research | Using GitHub Copilot increases experienced professional developers’ productivity on unfamiliar software engineering tasks. |
| b0016 | direct_fact | research | The United States Consumer Price Index measures price changes for a basket of consumer goods and services. |
| b0017 | direct_fact | research | Nominal gross domestic product removes the effects of price inflation from measured economic output. |
| b0018 | direct_fact | research | The euro, introduced as physical banknotes and coins in 2001, is the shared currency of the euro area. |
| b0019 | insufficient | **decline** | A United States federal minimum wage of $25 per hour in 2030 would increase total national employment during that year. |
| b0020 | conflict | research | New Jersey’s April 1992 minimum wage increase reduced employment at fast-food restaurants relative to eastern Pennsylvania. |
| b0021 | direct_fact | research | The Berlin Wall opened to cross-border travel on 9 November 1989. |
| b0022 | direct_fact | research | The Magna Carta of 1215 was issued during the reign of King Henry VIII of England. |
| b0023 | direct_fact | research | The Rosetta Stone, discovered in Egypt in 1798, helped scholars decipher Egyptian hieroglyphs. |
| b0024 | insufficient | research | The unidentified author known as Jack the Ripper was the painter Walter Sickert. |
| b0025 | conflict | research | The Bronze Age eruption of Thera occurred before 1600 BCE. |
| b0026 | direct_fact | research | The Paris Agreement was adopted at the United Nations climate conference in December 2015. |
| b0027 | direct_fact | research | The United States Constitution sets a six-year term for members of the House of Representatives. |
| b0028 | direct_fact | research | The Montreal Protocol, adopted in 1986, regulates substances that deplete the ozone layer. |
| b0029 | insufficient | **decline** | A nationwide four-day working week enacted in India in 2030 would reduce annual carbon emissions by exactly 10 percent. |
| b0030 | conflict | research | United States right-to-carry handgun laws reduce the violent crime rate compared with retaining more restrictive carry laws. |
| n0001 | comparison | research | GPT-4 scored in the 90th percentile on the Uniform Bar Exam. |
| n0002 | comparison | research | Claude 3 Opus outperforms GPT-4 on the MMLU benchmark. |
| n0003 | comparison | research | Electric cars produce lower lifetime CO2 emissions than gasoline cars. |
| n0004 | direct_fact | research | Moderna's COVID-19 vaccine was 94% effective. |
| n0005 | causal | **decline** | Social media use causes depression in teenagers. |
| n0006 | causal | **decline** | Remote work reduced US labour productivity growth after 2020. |
| n0007 | causal | **decline** | The 20-year average global temperature will pass 1.5 °C above pre-industrial levels before 2035. |
| n0008 | interpretive | research | The 2008 financial crisis caused the worst recession since the Great Depression. |
| n0009 | interpretive | research | GPT-4 has passed the Turing test. |
| n0010 | insufficient | research | The Antikythera mechanism was built by Archimedes. |

## After both of you have pushed

I diff the two blind labels (agreement rate before discussion, per the README), then compare with Fable's
5 sealed drafts (b0001, b0020, n0001, n0004, n0005) to flag anything worth a second look. You reconcile
into `claims.json`; Pari breaks ties. Fable never decides a label.
