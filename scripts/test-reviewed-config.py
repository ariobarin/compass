#!/usr/bin/env python3
"""Focused tests for reviewed Codex config overlays."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("reviewed-config.py")
SPEC = importlib.util.spec_from_file_location("reviewed_config", MODULE_PATH)
assert SPEC and SPEC.loader
reviewed_config = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = reviewed_config
SPEC.loader.exec_module(reviewed_config)

REVIEWED = '''# reviewed fragment
model = "gpt-5.6-sol"
model_context_window = 272000
model_auto_compact_token_limit = 233000
approval_policy = "never"

[agents]
max_depth = 2

[notice]
hide_full_access_warning = true

[features.multi_agent_v2]
hide_spawn_agent_metadata = false
tool_namespace = "agents"
'''

LIVE = '''model = "old-model"
service_tier = "flex"
custom_root_value = "keep"

[agents]
max_depth = 1 # keep this comment
custom_agent_value = "keep"

[mcp_servers.example]
command = "machine-local-command"

[projects.'C:\\work\\example']
trust_level = "trusted"

[generated_marketplace]
last_refresh = "machine-local"
'''


class ReviewedConfigTests(unittest.TestCase):
    def evaluate(self, reviewed: str = REVIEWED, live: str | None = LIVE):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reviewed_path = root / "config.review.toml"
            live_path = root / "config.toml"
            reviewed_path.write_text(reviewed, encoding="utf-8", newline="")
            if live is not None:
                live_path.write_text(live, encoding="utf-8", newline="")
            return reviewed_config.evaluate(reviewed_path, live_path)

    def test_overlay_preserves_unreviewed_state(self):
        result = self.evaluate()
        self.assertTrue(result["changed"])
        self.assertEqual(result["changed_count"], 8)
        merged = result["merged_text"]
        self.assertIn('model = "gpt-5.6-sol"', merged)
        self.assertIn('service_tier = "flex"', merged)
        self.assertIn('custom_root_value = "keep"', merged)
        self.assertIn('max_depth = 2 # keep this comment', merged)
        self.assertIn('custom_agent_value = "keep"', merged)
        self.assertIn('[mcp_servers.example]', merged)
        self.assertIn("[projects.'C:\\work\\example']", merged)
        self.assertIn('[generated_marketplace]', merged)
        self.assertIn('[notice]', merged)
        self.assertIn('[features.multi_agent_v2]', merged)

    def test_second_overlay_is_byte_idempotent(self):
        first = self.evaluate()
        second = self.evaluate(live=first["merged_text"])
        self.assertFalse(second["changed"])
        self.assertEqual(second["changed_count"], 0)
        self.assertEqual(second["merged_text"], first["merged_text"])

    def test_missing_live_file_builds_managed_config(self):
        result = self.evaluate(live=None)
        self.assertTrue(result["changed"])
        self.assertFalse(result["live_exists"])
        self.assertEqual(result["reviewed_count"], 8)
        parsed = reviewed_config.tomllib.loads(result["merged_text"])
        self.assertEqual(parsed["model"], "gpt-5.6-sol")
        self.assertEqual(parsed["agents"]["max_depth"], 2)
        self.assertFalse(parsed["features"]["multi_agent_v2"]["hide_spawn_agent_metadata"])

    def test_verification_reports_missing_and_mismatch(self):
        live = LIVE.replace('model = "old-model"\n', '').replace('max_depth = 1', 'max_depth = 7')
        result = self.evaluate(live=live)
        by_path = {change["path"]: change for change in result["changes"]}
        self.assertEqual(by_path["model"]["kind"], "missing")
        self.assertEqual(by_path["agents.max_depth"]["kind"], "mismatch")
        self.assertEqual(by_path["agents.max_depth"]["actual"], "7")
        self.assertEqual(by_path["agents.max_depth"]["expected"], "2")

    def test_duplicate_reviewed_key_fails(self):
        with self.assertRaisesRegex(reviewed_config.ReviewedConfigError, "duplicate|invalid reviewed TOML"):
            self.evaluate(reviewed='model = "a"\nmodel = "b"\n')

    def test_duplicate_managed_live_key_fails(self):
        with self.assertRaisesRegex(reviewed_config.ReviewedConfigError, "invalid live config.toml|duplicate managed"):
            self.evaluate(reviewed='model = "a"\n', live='model = "b"\nmodel = "c"\n')

    def test_unsupported_reviewed_value_fails(self):
        with self.assertRaisesRegex(reviewed_config.ReviewedConfigError, "only strings, integers, and booleans"):
            self.evaluate(reviewed='models = ["a", "b"]\n', live='')

    def test_hash_inside_string_is_not_a_comment(self):
        result = self.evaluate(reviewed='label = "value # retained" # comment\n', live='label = "old"\n')
        self.assertEqual(result["merged_text"], 'label = "value # retained"\n')

    def test_unrelated_multiline_string_is_preserved(self):
        reviewed = 'model = "new"\n[agents]\nmax_depth = 2\n'
        live = (
            'model = "old"\n'
            'app_helper = """\n'
            '[agents]\n'
            'max_depth = 999\n'
            '"""\n'
            '[agents]\n'
            'max_depth = 1\n'
        )
        result = self.evaluate(reviewed, live)
        merged = result["merged_text"]
        self.assertIn('app_helper = """\n[agents]\nmax_depth = 999\n"""', merged)
        parsed = tomllib.loads(merged)
        self.assertEqual(parsed["model"], "new")
        self.assertEqual(parsed["agents"]["max_depth"], 2)

    def test_same_line_unrelated_multiline_string_does_not_hide_tables(self):
        reviewed = 'model = "new"\n[agents]\nmax_depth = 2\n'
        live = 'model = "old"\nhelper = """text"""\n[agents]\nmax_depth = 1\n'
        result = self.evaluate(reviewed, live)
        parsed = tomllib.loads(result["merged_text"])
        self.assertEqual(parsed["model"], "new")
        self.assertEqual(parsed["helper"], "text")
        self.assertEqual(parsed["agents"]["max_depth"], 2)

    def test_managed_multiline_value_fails_safely(self):
        with self.assertRaisesRegex(
            reviewed_config.ReviewedConfigError, "unsupported or ambiguous"
        ):
            self.evaluate(reviewed='model = "new"\n', live='model = """old"""\n')

    def test_crlf_is_preserved_for_insertions(self):
        result = self.evaluate(reviewed='model = "new"\n[agents]\nmax_depth = 2\n', live='model = "old"\r\n')
        self.assertIn('\r\n[agents]\r\nmax_depth = 2\r\n', result["merged_text"])
        self.assertNotIn('\n[agents]\n', result["merged_text"].replace('\r\n', ''))

    def test_existing_unsupported_managed_syntax_fails_safely(self):
        with self.assertRaisesRegex(reviewed_config.ReviewedConfigError, "unsupported or ambiguous"):
            self.evaluate(reviewed='[agents]\nmax_depth = 2\n', live='agents.max_depth = 1\n')


if __name__ == "__main__":
    unittest.main()
