#!/usr/bin/env python3
"""Check index or HEAD blobs without importing application code or printing secrets."""
import argparse
import ast
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


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracked", action="store_true", help="check HEAD instead of index")
    args = parser.parse_args()
    if args.tracked:
        names = git("ls-tree", "-rz", "--name-only", "HEAD")
    else:
        names = git("ls-files", "-z")
    paths = [p.decode("utf-8") for p in names.split(b"\0") if p]
    errors = []
    total = 0
    for path in paths:
        p = PurePosixPath(path)
        parts = [part.lower() for part in p.parts]
        example = p.parent == PurePosixPath("examples") and p.name.endswith(".example.json")
        forbidden = (
            any(part in PRIVATE_DIRS or part.endswith("-env") or "secret" in part for part in parts)
            or any(part.startswith(".cache") for part in parts)
            or (p.suffix.lower() in PRIVATE_SUFFIXES and not example)
            or (p.name.startswith(".env") and p.name != ".env.example")
            or p.name.lower().startswith("credentials")
            or ".sqlite" in p.name.lower() or ".db-" in p.name.lower()
            or p.name == ".DS_Store"
        )
        if forbidden:
            errors.append(f"{path}: private/runtime or binary path")
            continue
        ref = f"HEAD:{path}" if args.tracked else f":{path}"
        size = int(git("cat-file", "-s", ref))
        total += size
        if size > 1024 * 1024:
            errors.append(f"{path}: exceeds 1 MiB source limit")
            continue
        content = git("show", ref)
        if b"\0" in content:
            errors.append(f"{path}: unexpected binary content")
        if any(re.search(pattern, content) for pattern in SECRET_PATTERNS):
            errors.append(f"{path}: possible credential; review locally")
        if p.suffix == ".py":
            try:
                ast.parse(content, filename=path)
            except (SyntaxError, UnicodeError):
                errors.append(f"{path}: invalid Python syntax")
    if errors:
        print("Repository check failed (matched contents withheld):")
        print("\n".join(errors))
        return 1
    print(f"Checked {len(paths)} {'tracked' if args.tracked else 'staged'} files, {total:,} bytes: passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
