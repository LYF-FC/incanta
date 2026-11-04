# Contributing

Start with the [development workflow](docs/DEVELOPMENT.md), [constitution](.specify/memory/constitution.md) and [roadmap](ROADMAP.md). Use synthetic inputs. Keep the repository private.

## Change workflow

1. Pick one issue or roadmap outcome. Read the audit and relevant feature directory.
2. Create or resume a feature specification; agree acceptance criteria before implementing. Small documentation/tooling fixes can reference the constitution and PR instead of creating a new product feature.
3. Use a branch and a pull request into `main`. Match feature branch names to `specs/<number>-<name>` when practical; tooling branches may use `chore/<name>`.
4. Implement the smallest coherent slice. Add meaningful tests for behavior or safeguards; use fake inference and temporary storage by default.
5. Stage explicit reviewed paths, run the checks below, inspect the staged diff locally and commit.
6. Link the feature spec/issue in the PR. State test results and remaining limitations. Merge after checks pass, then update milestone/spec status honestly.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py

git diff --cached --check
git diff --cached --stat
```

The checker reads index blobs, including existing staged content, not unstaged changes. After a commit use `--tracked` to check HEAD. Never stage private files with `git add -f`. Do not rewrite shared history or force-push without the owner's explicit agreement.

## Done means

Acceptance criteria have evidence; relevant automated checks pass; setup/contracts/docs reflect behavior; private data and models are absent from the staged diff; remaining manual checks are named. Completing a specification is not completing its implementation. The present CI checks repository safeguards and syntax, not model quality or full application behavior.

CODEOWNERS and review are conventions. GitHub reports that protected branches/rulesets for this private repository require a plan upgrade; this setup keeps the repository private and does not change the account plan. No enforced owner-review requirement is assumed. No Incanta redistribution license has been selected; see [third-party notices](THIRD_PARTY_NOTICES.md) before redistributing bundled tooling.
