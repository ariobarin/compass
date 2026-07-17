from __future__ import annotations

from _test_orchestration_ledger_common import *

class OrchestrationLedgerTests1(unittest.TestCase):
    def test_status_reports_absent_without_creating_state(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                code, stdout, stderr = run_cli("--root", str(root), "status", "--json")
                self.assertEqual(code, 0, stderr)
                self.assertFalse(json.loads(stdout)["present"])
                self.assertFalse((root / ".local").exists())

    def test_control_lifecycle_and_private_file(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "release")
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-owner",
                        "--goal-id",
                        "release",
                        "--execution-owner",
                        "worker-2",
                        "--worker-id",
                        "thread-2",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-next",
                        "--goal-id",
                        "release",
                        "--action",
                        "Run final proof",
                        "--check-at",
                        "2026-07-12T12:00:00Z",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "add-evidence",
                        "--goal-id",
                        "release",
                        "--kind",
                        "test",
                        "--summary",
                        "Checks passed",
                        "--locator",
                        "run:835",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-gate",
                        "--goal-id",
                        "release",
                        "--gate",
                        "authorized",
                        "--action",
                        "merge PR 42",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-decision",
                        "--goal-id",
                        "release",
                        "--question",
                        "Which channel?",
                        "--option",
                        "stable",
                        "--option",
                        "beta",
                    )[0],
                    0,
                )
                code, stdout, error = run_cli(
                    "--root",
                    str(root),
                    "status",
                    "--goal-id",
                    "release",
                    "--json",
                )
                self.assertEqual(code, 0, error)
                goal = json.loads(stdout)["goals"][0]
                self.assertEqual(goal["execution_owner"], "worker-2")
                self.assertEqual(goal["worker_id"], "thread-2")
                self.assertEqual(goal["next_action"], "Run final proof")
                self.assertEqual(goal["public_mutation_action"], "merge PR 42")
                self.assertEqual(goal["decision_needed"]["options"], ["stable", "beta"])
                self.assertEqual(run_cli("--root", str(root), "validate")[0], 0)
                if os.name != "nt":
                    mode = stat.S_IMODE(
                        (root / ".local" / "orchestration-ledger.json").stat().st_mode
                    )
                    self.assertEqual(mode, 0o600)

    def test_complete_requires_evidence_and_no_open_work(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "proof")
                code, _, error = run_mutation(
                    root,
                    "set-state",
                    "--goal-id",
                    "proof",
                    "--state",
                    "complete",
                )
                self.assertEqual(code, 1)
                self.assertIn("requires completion evidence", error)
                self.assertEqual(
                    run_mutation(
                        root,
                        "add-evidence",
                        "--goal-id",
                        "proof",
                        "--kind",
                        "test",
                        "--summary",
                        "Final condition passed",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-next",
                        "--goal-id",
                        "proof",
                        "--clear",
                    )[0],
                    0,
                )
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-state",
                        "--goal-id",
                        "proof",
                        "--state",
                        "complete",
                    )[0],
                    0,
                )

    def test_duplicate_goal_and_invalid_timestamp_are_rejected(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "same")
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "init",
                    "--goal-id",
                    "same",
                    "--goal",
                    "Duplicate",
                    "--execution-owner",
                    "worker",
                )
                self.assertEqual(code, 1)
                self.assertIn("goal already exists", error)
                code, _, error = run_mutation(
                    root,
                    "set-next",
                    "--goal-id",
                    "same",
                    "--action",
                    "Wake later",
                    "--check-at",
                    "tomorrow",
                )
                self.assertEqual(code, 1)
                self.assertIn("ISO 8601", error)

    def test_ledger_path_escape_and_symlink_are_rejected(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "--ledger",
                    str(root / "outside.json"),
                    "status",
                )
                self.assertEqual(code, 1)
                self.assertIn("must stay under", error)
                target = root / "target"
                target.mkdir()
                try:
                    (root / ".local").symlink_to(target, target_is_directory=True)
                except OSError:
                    return
                code, _, error = run_cli("--root", str(root), "status")
                self.assertEqual(code, 1)
                self.assertIn("must not traverse a symlink", error)

    def test_authorization_revision_and_exact_grants(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_goal(root, "auth")
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "set-state",
                    "--goal-id",
                    "auth",
                    "--state",
                    "waiting",
                    "--actor",
                    "intruder",
                    "--expected-revision",
                    "1",
                )
                self.assertEqual(code, 1)
                self.assertIn("not authorized", error)
                self.assertEqual(
                    run_mutation(
                        root,
                        "set-grant",
                        "--goal-id",
                        "auth",
                        "--grant-actor",
                        "runner",
                        "--mutation",
                        "set-state",
                    )[0],
                    0,
                )
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "set-state",
                    "--goal-id",
                    "auth",
                    "--state",
                    "waiting",
                    "--actor",
                    "runner",
                    "--expected-revision",
                    "2",
                )
                self.assertEqual(code, 0, error)
                code, _, error = run_cli(
                    "--root",
                    str(root),
                    "set-state",
                    "--goal-id",
                    "auth",
                    "--state",
                    "active",
                    "--actor",
                    "controller",
                    "--expected-revision",
                    "1",
                )
                self.assertEqual(code, 1)
                self.assertIn("stale control revision", error)
