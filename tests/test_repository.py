"""Regression tests for privacy safeguards, with synthetic blobs and isolated Git."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / "scripts/check_repository.py"
spec = importlib.util.spec_from_file_location("repository_guard", CHECKER)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class BlobChecks(unittest.TestCase):
    def test_source_and_shared_constitution_are_allowed(self):
        for name in ["backend/memory_manager.py", ".specify/memory/constitution.md"]:
            with self.subTest(name=name):
                self.assertEqual(guard.inspect_blob(name, b"# synthetic source\n"), [])

    def test_metadata_exceptions_are_exact(self):
        for name in guard.SHARED_METADATA:
            with self.subTest(name=name):
                self.assertEqual(guard.inspect_blob(name, b"{}"), [])
        for name in [".specify/private.json", ".specify/memory/history.json",
                     ".specify/memory/notes.md", "backend/personalities/example.json"]:
            with self.subTest(name=name):
                self.assertTrue(guard.inspect_blob(name, b"{}"))

    def test_local_tool_state_is_rejected(self):
        for name in [".specify/feature.json", ".specify/extensions/git/local-config.yml",
                     ".specify/integrations/packages/adapter.py", ".codex/config.toml",
                     ".agents/auth.txt", ".agents/skills/speckit-specify/session.txt"]:
            with self.subTest(name=name):
                self.assertTrue(guard.inspect_blob(name, b"synthetic"))
        self.assertEqual(guard.inspect_blob(".agents/skills/speckit-specify/SKILL.md", b"text"), [])

    def test_private_assets_and_runtime_files_are_rejected(self):
        for name in ["models/model.gguf", "diffusion_pytorch_model.bin", "weights.safetensors",
                     "chat_histories/events.txt", "personalities/character.md", ".env",
                     "data/events.csv", "cache/example.py", "generated_images/event.json",
                     "history.sqlite-wal", "incanta-env/example.py"]:
            with self.subTest(name=name):
                self.assertTrue(guard.inspect_blob(name, b"synthetic"))

    def test_metadata_and_examples_still_get_content_checks(self):
        token = ("ghp_" + "A" * 36).encode()
        for name in ["examples/personality.example.json", ".specify/init-options.json"]:
            with self.subTest(name=name):
                errors = guard.inspect_blob(name, b'{"value":"' + token + b'"}')
                self.assertTrue(any("possible credential" in error for error in errors))
                self.assertNotIn(token.decode(), "\n".join(errors))
                self.assertTrue(guard.inspect_blob(name, b"{broken"))

    def test_python_binary_size_and_git_mode_checks(self):
        self.assertTrue(guard.inspect_blob("example.py", b"answer = (\n"))
        self.assertTrue(guard.inspect_blob("example.txt", b"a\0b"))
        self.assertTrue(guard.inspect_blob("example.txt", b"a" * (1024 * 1024 + 1)))
        self.assertTrue(guard.inspect_blob("linked.txt", b"target", "120000"))
        self.assertTrue(guard.inspect_blob("submodule", b"", "160000"))


class GitBlobIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="incanta-guard-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        for key in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"]:
            self.env.pop(key, None)
        self.git("init", "-q")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env,
                              check=True, capture_output=True, text=True)

    def check(self, *args):
        return subprocess.run([sys.executable, str(CHECKER), *args], cwd=self.root,
                              env=self.env, capture_output=True, text=True)

    def write(self, name, content):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)

    def test_scans_staged_blobs_instead_of_unstaged_worktree(self):
        token = ("ghp_" + "B" * 36).encode()
        self.write("safe.txt", token)
        self.git("add", "safe.txt")
        self.write("safe.txt", b"clean working copy")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("possible credential", result.stdout)
        self.assertNotIn(token.decode(), result.stdout + result.stderr)
        self.git("add", "safe.txt")
        self.write("safe.txt", token)
        self.assertEqual(self.check().returncode, 0)

    def test_tracked_mode_uses_head_instead_of_index(self):
        self.write("safe.py", b"answer = 42\n")
        self.git("add", "safe.py")
        self.git("-c", "user.name=Synthetic Test", "-c", "user.email=test@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "synthetic baseline")
        self.write("history.json", b"{}")
        self.git("add", "history.json")
        self.assertEqual(self.check().returncode, 1)
        self.assertEqual(self.check("--tracked").returncode, 0)

    def test_forced_private_file_and_symlink_are_rejected(self):
        self.write(".gitignore", b"*.json\n")
        self.write("chat_histories/history.json", b"{}")
        self.git("add", "-f", "chat_histories/history.json")
        self.assertEqual(self.check().returncode, 1)
        self.git("rm", "--cached", "chat_histories/history.json")
        self.write("safe.txt", b"synthetic")
        (self.root / "linked.txt").symlink_to("safe.txt")
        self.git("add", "linked.txt")
        self.assertEqual(self.check().returncode, 1)


if __name__ == "__main__":
    unittest.main()
