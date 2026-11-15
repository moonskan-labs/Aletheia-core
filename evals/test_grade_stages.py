"""Tests for grade_stages.py: an oracle run must pass every stage, broken runs must drop
at the stage that broke, and nothing that failed to produce an answer may count as right."""

import copy
import unittest

from grade_stages import grade_case, normalize_url, quote_found, rate, summarize

URL = "https://www.nasa.gov/mission/apollo-11/"
QUOTE = "the lunar module Eagle landed in the Sea of Tranquility on July 20, 1969"

CASE = {
    "id": "t0001",
    "case_type": "direct_fact",
    "expected": {"outcome": "decided", "verdict": "true", "unable_to_decide_reason": None},
    "acceptable_alternatives": [],
    "expected_flags": [],
    "key_sources": [{"url": URL, "shows": "NASA mission page gives the landing date."}],
}
KEYS = {
    "key_sources": [{"urls": [URL], "decisive_quotes": [QUOTE], "expected_relation": "supports"}],
    "expected_route": "research",
}


def event(kind, **payload):
    return {"type": kind, "payload": payload}


def oracle():
    """A run that does everything right."""
    return {
        "id": "t0001",
        "investigation": {
            "status": "completed",
            "stop_reason": "completed",
            "result": {
                "outcome": "decided",
                "verdict": "true",
                "unable_to_decide_reason": None,
                "finding": {"qualification_flags": []},
                "explanation": [{"text": "NASA records the landing.", "evidence_ids": ["e1"]}],
            },
        },
        "evidence": {
            "sources": [{"id": "s1", "url": "http://nasa.gov/mission/apollo-11", "limitations": []}],
            "evidence": [
                {
                    "id": "e1",
                    "admissible": True,
                    "assessment": {"citation": {"snapshot_id": "s1"}, "relation": "supports"},
                    "excerpts": [{"text": "On July 20, 1969, the lunar module **Eagle** landed in the\nSea of Tranquility."}],
                }
            ],
        },
        "events": [
            event("claim_interpreted", assertion_id="a1"),
            event("source_selected", url=URL + "?utm_source=x"),
            event("source_extracted", url=URL),
        ],
        "network_attempts": [{"provider": "nebius"}, {"provider": "tavily"}],
    }


class Normalization(unittest.TestCase):
    def test_url_variants_match(self):
        self.assertEqual(normalize_url(URL), normalize_url("http://nasa.gov/mission/apollo-11#top"))
        self.assertNotEqual(normalize_url(URL), normalize_url("https://nasa.gov/mission/apollo-12/"))

    def test_quote_survives_formatting_and_small_changes(self):
        page = "On July 20, 1969, the lunar module **Eagle** landed in the\nSea of Tranquility."
        self.assertTrue(quote_found("lunar module Eagle landed in the Sea of Tranquility", page))
        self.assertFalse(quote_found("lunar module Eagle landed in the Ocean of Storms", page))
        self.assertFalse(quote_found(QUOTE, ""))

    def test_scattered_words_do_not_count(self):
        page = "Eagle " + "filler " * 200 + "lunar module " + "filler " * 200 + "landed Tranquility"
        self.assertFalse(quote_found("lunar module Eagle landed in the Sea of Tranquility", page))


class Stages(unittest.TestCase):
    def test_oracle_passes_every_stage(self):
        row = grade_case(CASE, oracle(), KEYS)
        self.assertTrue(all(row["stages"].values()), row["stages"])
        self.assertIsNone(row["dropped_at"])
        self.assertTrue(row["correct"])
        self.assertEqual(row["usage"]["tavily_calls"], 1)

    def test_null_run_drops_at_ran_and_is_wrong(self):
        for null in ({}, {"id": "t0001", "runner_error": "capture_failed"}):
            row = grade_case(CASE, null, KEYS)
            self.assertEqual(row["dropped_at"], "ran")
            self.assertIs(row["correct"], False)

    def test_needs_clarification_drops_at_interpretation(self):
        a = oracle()
        a["investigation"].update(status="needs_clarification", result=None)
        self.assertEqual(grade_case(CASE, a, KEYS)["dropped_at"], "interpretation")

    def trail(self, a, keys=KEYS):
        return grade_case(CASE, a, keys)["detail"]["trail_ended_at"]

    def test_key_source_never_selected(self):
        a = oracle()
        a["events"][1] = event("source_selected", url="https://en.wikipedia.org/wiki/Apollo_11")
        self.assertEqual(self.trail(a), "search_selected")

    def test_correct_answer_from_unlisted_sources_is_not_a_drop_out(self):
        a = oracle()
        a["events"][1] = event("source_selected", url="https://en.wikipedia.org/wiki/Apollo_11")
        row = grade_case(CASE, a, KEYS)
        self.assertIsNone(row["dropped_at"])
        self.assertIs(row["correct"], True)

    def test_wrong_answer_drops_at_the_source_stage_that_broke(self):
        a = oracle()
        a["events"][1] = event("source_selected", url="https://en.wikipedia.org/wiki/Apollo_11")
        a["investigation"]["status"] = "partial"
        row = grade_case(CASE, a, KEYS)
        self.assertEqual(row["dropped_at"], "search_selected")
        self.assertIs(row["correct"], False)

    def test_other_page_on_the_key_site_counts(self):
        a = oracle()
        a["events"][1] = event("source_selected", url="https://www.nasa.gov/wp-content/apollo11-press-kit.pdf")
        self.assertTrue(grade_case(CASE, a, {})["stages"]["search_selected"])

    def test_empty_sites_requires_the_exact_page(self):
        a = oracle()
        a["events"][1] = event("source_selected", url="https://www.nasa.gov/other-page/")
        keys = {"key_sources": [{**KEYS["key_sources"][0], "sites": []}]}
        self.assertEqual(self.trail(a, keys), "search_selected")

    def test_selected_but_not_extracted(self):
        a = oracle()
        a["evidence"]["sources"] = []
        self.assertEqual(self.trail(a), "extracted")

    def test_decisive_passage_lost(self):
        a = oracle()
        a["evidence"]["evidence"][0]["excerpts"] = [{"text": "Skip to main content. Missions menu."}]
        self.assertEqual(self.trail(a), "passage_selection")

    def test_decisive_passage_rejected_in_assessment(self):
        a = oracle()
        a["evidence"]["evidence"][0].update(admissible=False, rejection_reason="scope_mismatch")
        self.assertEqual(self.trail(a), "assessment")

    def test_wrong_relation_fails_assessment(self):
        a = oracle()
        a["evidence"]["evidence"][0]["assessment"]["relation"] = "contradicts"
        self.assertEqual(self.trail(a), "assessment")

    def test_partial_run_is_wrong_even_with_matching_label(self):
        a = oracle()
        a["investigation"]["status"] = "partial"
        row = grade_case(CASE, a, KEYS)
        self.assertEqual(row["dropped_at"], "final_answer")
        self.assertIs(row["correct"], False)

    def test_wrong_verdict(self):
        a = oracle()
        a["investigation"]["result"]["verdict"] = "false"
        self.assertEqual(grade_case(CASE, a, KEYS)["dropped_at"], "final_answer")

    def test_acceptable_alternative_counts(self):
        a = oracle()
        a["investigation"]["result"]["verdict"] = "almost"
        case = copy.deepcopy(CASE)
        case["acceptable_alternatives"] = [{"outcome": "decided", "verdict": "almost", "unable_to_decide_reason": None}]
        row = grade_case(case, a, KEYS)
        self.assertTrue(row["correct"])
        self.assertEqual(row["detail"]["almost_correction"], "needs_judge")

    def test_citation_to_inadmissible_or_missing_evidence(self):
        a = oracle()
        a["investigation"]["result"]["explanation"].append({"text": "Also true.", "evidence_ids": ["nope"]})
        row = grade_case(CASE, a, KEYS)
        self.assertEqual(row["dropped_at"], "citations")
        self.assertEqual(row["detail"]["citations_valid"], "1/2")

    def test_missing_quote_key_leaves_passage_ungraded_not_failed(self):
        row = grade_case(CASE, oracle(), {})  # falls back to the claim's key_sources URLs
        self.assertIsNone(row["stages"]["passage_selection"])
        self.assertIsNone(row["dropped_at"])
        self.assertTrue(row["correct"])

    def test_flags_scored(self):
        a = oracle()
        a["investigation"]["result"]["finding"]["qualification_flags"] = [{"type": "narrow_scope", "dimension": "population"}]
        self.assertEqual(grade_case(CASE, a, KEYS)["detail"]["flags"], {"tp": 0, "fp": 1, "fn": 0})


class Declines(unittest.TestCase):
    def declined(self):
        a = oracle()
        a["investigation"].update(status="completed", stop_reason="unsupported_method", result=None,
                                  method_limitation={"kind": "causal"})
        return a

    def test_correct_decline(self):
        row = grade_case(CASE, self.declined(), {"expected_route": "decline"})
        self.assertTrue(row["correct"])
        self.assertIsNone(row["dropped_at"])

    def test_researching_a_decline_case_is_wrong(self):
        row = grade_case(CASE, oracle(), {"expected_route": "decline"})
        self.assertIs(row["correct"], False)
        self.assertEqual(row["detail"]["route"], "researched_instead_of_declining")

    def test_declining_a_researchable_claim_is_wrong_not_factual(self):
        row = grade_case(CASE, self.declined(), KEYS)
        self.assertEqual(row["dropped_at"], "interpretation")
        self.assertIs(row["correct"], False)


class Summary(unittest.TestCase):
    def test_funnel_and_accuracy(self):
        rows = [grade_case(CASE, oracle(), KEYS), grade_case(CASE, {}, KEYS)]
        s = summarize(rows)
        self.assertEqual(s["passed_stage"]["ran"], 1)
        self.assertEqual(s["dropped_at"], {"ran": 1})
        self.assertEqual(s["label_accuracy_completed"]["k"], 1)
        self.assertEqual(s["label_accuracy_overall"]["n"], 2)

    def test_wilson_interval(self):
        self.assertIsNone(rate(0, 0)["rate"])
        r = rate(1, 40)
        self.assertLess(r["ci95"][0], 0.025)
        self.assertGreater(r["ci95"][1], 0.1)


if __name__ == "__main__":
    unittest.main()
