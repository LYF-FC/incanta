#!/usr/bin/env python3
"""Check index or HEAD blobs without importing application code or printing secrets."""
import argparse
import ast
import json
import re
import subprocess
from pathlib import PurePosixPath


PRIVATE_DIRS = {
    "personalities", "chat_histories", "memories", "memory", "histories",
    "sessions", "data", "models", "checkpoints", "loras", "embeddings",
    "comfyui", "generated_images", "output", "outputs", "input", "temp",
    "venv", ".venv", "env", "node_modules", "__pycache__", "logs", ".cache", "cache", ".tox", ".nox",
}
PRIVATE_SUFFIXES = {
    ".gguf", ".ggml", ".safetensors", ".ckpt", ".pt", ".pth", ".bin",
    ".onnx", ".h5", ".hdf5", ".db", ".sqlite", ".sqlite3", ".json",
    ".jsonl", ".ndjson", ".log", ".pem", ".key", ".p12", ".pfx",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".wav",
    ".mp3", ".zip", ".gz", ".tar", ".7z", ".bak", ".backup", ".pyc",
}
SECRET_PATTERNS = [
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    rb"gh[pousr]_[A-Za-z0-9]{20,}",
    rb"github_pat_[A-Za-z0-9_]{30,}",
    rb"AKIA[0-9A-Z]{16}",
    rb"sk-[A-Za-z0-9_-]{24,}",
    rb"(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*[\"'][^\"'\r\n]{8,}[\"']",
]

# Deliberately exact: no blanket exemption for .specify/ or personality JSON.
SHARED_METADATA = {
    ".specify/init-options.json",
    ".specify/integration.json",
    ".specify/integrations/codex.manifest.json",
    ".specify/integrations/speckit.manifest.json",
    ".specify/memory/.constitution-template.json",
    ".specify/workflows/workflow-registry.json",
}
SHARED_MEMORY_FILES = {
    ".specify/memory/constitution.md",
    ".specify/memory/.constitution-template.json",
}


def inspect_blob(path, content, mode="100644"):
    """Return safe diagnostics for one Git blob; never echo matched content."""
    p = PurePosixPath(path)
    parts = [part.lower() for part in p.parts]
    example = p.parent == PurePosixPath("examples") and p.name.endswith(".example.json")
    metadata = path in SHARED_METADATA
    forbidden_dir = any(
        (part in PRIVATE_DIRS and not (part == "memory" and path in SHARED_MEMORY_FILES))
        or part.endswith("-env") or "secret" in part or part.startswith(".cache")
        for part in parts
    )
    local_spec_state = (
        path == ".specify/feature.json"
        or (path.startswith(".specify/extensions/") and p.name == "local-config.yml")
        or path.startswith(".specify/integrations/packages/")
        or path == ".specify/integrations/packages.json"
    )
    local_agent_state = (
        path.startswith(".codex/")
        or (path.startswith(".agents/") and not (
            len(p.parts) == 4 and p.parts[1] == "skills"
            and p.parts[2].startswith("speckit-") and p.name == "SKILL.md"
        ))
    )
    if (
        forbidden_dir or local_spec_state or local_agent_state
        or (p.suffix.lower() in PRIVATE_SUFFIXES and not (example or metadata))
        or (p.name.startswith(".env") and p.name != ".env.example")
        or p.name.lower().startswith("credentials")
        or ".sqlite" in p.name.lower() or ".db-" in p.name.lower()
        or p.name == ".DS_Store"
    ):
        return [f"{path}: private/runtime or binary path"]
    if mode not in {"100644", "100755"}:
        return [f"{path}: symlinks and submodules are not allowed"]
    if len(content) > 1024 * 1024:
        return [f"{path}: exceeds 1 MiB source limit"]
    errors = []
    if b"\0" in content:
        errors.append(f"{path}: unexpected binary content")
    if any(re.search(pattern, content) for pattern in SECRET_PATTERNS):
        errors.append(f"{path}: possible credential; review locally")
    if metadata or example:
        try:
            json.loads(content)
        except (ValueError, UnicodeError):
            errors.append(f"{path}: invalid JSON")
    if p.suffix == ".py":
        try:
            ast.parse(content, filename=path)
        except (SyntaxError, UnicodeError):
            errors.append(f"{path}: invalid Python syntax")
    return errors


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracked", action="store_true", help="check HEAD instead of index")
    args = parser.parse_args()
    if args.tracked:
        entries = git("ls-tree", "-rz", "HEAD")
    else:
        entries = git("ls-files", "--stage", "-z")
    paths = []
    for entry in entries.split(b"\0"):
        if entry:
            info, path = entry.split(b"\t", 1)
            paths.append((path.decode("utf-8"), info.split()[0].decode("ascii")))
    errors = []
    total = 0
    for path, mode in paths:
        if mode not in {"100644", "100755"}:
            errors.append(f"{path}: symlinks and submodules are not allowed")
            continue
        ref = f"HEAD:{path}" if args.tracked else f":{path}"
        size = int(git("cat-file", "-s", ref))
        total += size
        if size > 1024 * 1024:
            errors.append(f"{path}: exceeds 1 MiB source limit")
            continue
        errors.extend(inspect_blob(path, git("show", ref), mode))
    if errors:
        print("Repository check failed (matched contents withheld):")
        print("\n".join(errors))
        return 1
    print(f"Checked {len(paths)} {'tracked' if args.tracked else 'staged'} files, {total:,} bytes: passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
