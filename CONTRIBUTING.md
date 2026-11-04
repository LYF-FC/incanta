# Contributing

Keep changes small and reviewable. Use a branch for new behavior and a pull request into `main`; these are project conventions, not enforced branch protection.

Before committing:

1. Use synthetic inputs and examples. Keep models, private character definitions, conversations, runtime data and credentials outside Git.
2. Stage specific reviewed paths. Avoid `git add -f` and indiscriminate staging of recovered folders.
3. Run `python3 scripts/check_repository.py` and inspect `git diff --cached` locally. The script checks staged content and never prints credential matches.
4. Document behavior changes and meaningful verification. A syntax check does not prove model inference works.

Do not rewrite shared history or force-push without explicit maintainer agreement. Keep the repository private. Preserve the original dependency snapshot until a separately reviewed dependency cleanup.

No open-source license is selected; obtain the owner's permission before redistribution.
