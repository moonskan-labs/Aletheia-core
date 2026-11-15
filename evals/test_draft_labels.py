"""Offline tests for draft_labels.py: no network, no SDK, no key."""

import datetime as dt
import json
import unittest
from types import SimpleNamespace

from draft_labels import LABELER, check_draft, cost_usd, fetched_pages, final_json, user_prompt

URL = "https://www.archives.gov/publications/prologue/2003/summer/20-july-1969.html"
PAGE = "At 4:17 p.m. EDT on July 20, 1969, the lunar module Eagle landed on the Moon."
CASE = {"id": "b0001", "claim": "The Apollo 11 lunar module landed on the Moon on 20 July 1969.",
        "case_type": "direct_fact", "context": {}, "route_hint": "research"}


def draft(quote="the lunar module Eagle landed on the Moon", **record_changes):
    record = {
        "id": "b0001", "split": "tuning", "claim": CASE["claim"], "context": {}, "case_type": "direct_fact",
        "expected": {"outcome": "decided", "verdict": "true", "unable_to_decide_reason": None,
                     "expected_correction": None},
        "acceptable_alternatives": [], "expected_flags": [],
        "key_sources": [{"url": URL, "shows": "The National Archives records the landing date."}],
        "as_of": dt.date.today().isoformat(), "labelers": [LABELER], "status": "draft",
        "reviewer_note": "Primary record gives the date.",
    }
    record.update(record_changes)
    return {"record": record, "stage_keys": {"key_sources": [
        {"urls": [URL], "sites": ["archives.gov"], "decisive_quotes": [quote], "expected_relation": "supports"}]},
        "notes_for_reviewers": "Easy."}


def fetch_message(url=URL, text=PAGE):
    return {"role": "assistant", "content": [{"type": "web_fetch_tool_result", "content": {
        "type": "web_fetch_result", "url": url,
        "content": {"type": "document", "source": {"type": "text", "data": text}}}}]}


class Parsing(unittest.TestCase):
    def test_last_json_block_wins(self):
        content = [SimpleNamespace(type="text", text='Draft:\n```json\n{"a": 1}\n```\nFixed:\n```json\n{"a": 2}\n```')]
        self.assertEqual(final_json(content), {"a": 2})

    def test_no_json_block_is_an_error(self):
        with self.assertRaises(ValueError):
            final_json([SimpleNamespace(type="text", text="I could not decide.")])

    def test_fetched_pages_reads_text_documents(self):
        pages = fetched_pages([{"role": "user", "content": "hi"}, fetch_message()])
        self.assertEqual(list(pages.values()), [PAGE])

    def test_query_string_ignored_and_pdf_marked(self):
        pdf = {"role": "assistant", "content": [{"type": "web_fetch_tool_result", "content": {
            "type": "web_fetch_result", "url": "https://x.org/p.pdf",
            "content": {"type": "document", "source": {"type": "base64", "data": "JVBER"}}}}]}
        pages = fetched_pages([fetch_message(url=URL + "?s_cid=abc"), pdf])
        _, checks = check_draft(CASE, draft(), pages)
        self.assertTrue(checks[0]["verbatim_on_fetched_page"])
        self.assertIsNone(pages["x.org/p.pdf"])


class Checks(unittest.TestCase):
    pages = fetched_pages([fetch_message()])

    def test_valid_draft_with_verbatim_quote(self):
        problems, checks = check_draft(CASE, draft(), self.pages)
        self.assertEqual(problems, [])
        self.assertTrue(checks[0]["verbatim_on_fetched_page"])

    def test_invented_quote_is_reported_not_blocking(self):
        problems, checks = check_draft(CASE, draft(quote="Eagle landed in the Ocean of Storms at dawn"), self.pages)
        self.assertEqual(problems, [])
        self.assertFalse(checks[0]["verbatim_on_fetched_page"])

    def test_quote_from_a_page_never_fetched(self):
        _, checks = check_draft(CASE, draft(), {})
        self.assertFalse(checks[0]["page_fetched"])

    def test_changed_claim_is_rejected(self):
        problems, _ = check_draft(CASE, draft(claim="Apollo 11 landed in 1970 on the Moon."), self.pages)
        self.assertTrue(any("record.claim" in p for p in problems))

    def test_human_labeler_name_is_rejected(self):
        problems, _ = check_draft(CASE, draft(labelers=["chandra"]), self.pages)
        self.assertTrue(any("labelers" in p for p in problems))

    def test_almost_without_correction_fails_validator_rules(self):
        bad = {"outcome": "decided", "verdict": "almost", "unable_to_decide_reason": None, "expected_correction": None}
        problems, _ = check_draft(CASE, draft(expected=bad), self.pages)
        self.assertTrue(problems)

    def test_bad_relation(self):
        d = draft()
        d["stage_keys"]["key_sources"][0]["expected_relation"] = "irrelevant"
        problems, _ = check_draft(CASE, d, self.pages)
        self.assertTrue(any("expected_relation" in p for p in problems))


class Prompt(unittest.TestCase):
    def test_prompt_carries_fixed_fields_and_decline_hint(self):
        text = user_prompt({**CASE, "route_hint": "decline"}, "2026-11-12")
        self.assertIn('"labelers": [\n    "fable-5-2"', text)
        self.assertIn("decline", text)
        self.assertIn(json.dumps(CASE["claim"]), text)


class Cost(unittest.TestCase):
    def test_cost_formula(self):
        usage = {"input_tokens": 1_000_000, "output_tokens": 100_000,
                 "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1_000_000}
        self.assertAlmostEqual(cost_usd(usage, searches=10), 8 + 4 + 0.2 + 0.1)


if __name__ == "__main__":
    unittest.main()
