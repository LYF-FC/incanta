# Verification strategy

## Available now

`python3 -m unittest discover -s tests -v` exercises repository guard behavior with synthetic data and temporary Git repositories. `python3 scripts/check_repository.py` scans index blobs; `--tracked` scans HEAD. It checks private/runtime paths, binary/large blobs, selected credential patterns, exact JSON exceptions and Python syntax. It never prints credential matches.

GitHub Actions runs that suite on Python 3.11 and 3.13, parses tracked Python through the guard, checks JavaScript with `node --check` and Bash helpers with `bash -n`. It does not install historical app requirements or use model weights. A passing run certifies only these checks.

## Required for specification 001

Introduce a fake inference adapter and temporary memory storage, then test app startup/readiness, request contracts, malformed input, exactly-once turn persistence, atomic-write failures, deterministic emotion precedence, overlapping requests and frontend literal rendering/error states. Follow the feature tasks for file paths and requirement traceability.

A manual real-model smoke test is a separate exit gate: record date, runtime versions, OS/hardware, model identifier/revision/checksum, command/settings without private paths and pass/fail. Verify one response, one stored event and a restart. Do not commit private inputs/outputs, histories or model files. Until that check happens, the app remains unverified.

## Scope of the repository guard

It detects common patterns, not arbitrary private prose or every possible credential format. Metadata allowlisting permits only particular paths, not secret contents. Review staged files manually. The guard does not scan all historical commits or audit installed packages. Runtime schemas, migrations and model safety/quality belong to later feature verification.
