# Implementation Plan: Reproducible local companion MVP

**Branch**: `codex/005-local-mvp-release` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Status:** planned only. Requires component acceptance from 001–004; planning does not close their gates.

## Summary

Keep existing app stack. Add consistent local backup/restore commands, a combined synthetic acceptance suite and an owner-run Mac release checklist. Review runtime dependencies in this dedicated feature, keeping historical requirements.txt unchanged. Use owner-approved evidence to gate release, not task counts.

## Technical Context

**Language/Version:** Python 3.11/3.13, plain JS; target native runtime pinned from measured Mac compatibility.

**Primary Dependencies:** existing app/runtime requirements, sqlite3 backup API and stdlib hashing/filesystem; renderer/helper installed separately and explicitly.

**Storage:** 002–004 DB/private files, private versioned backup directories, sanitized shared acceptance evidence.

**Testing:** unittest/Node, synthetic restored state in separate temp roots; manual native model/render/Mac notification gates.

**Target Platform:** M2 MacBook Pro/16 GB; no inferred Mac mini/Nomad certification.

**Project Type:** current local app with maintenance CLI.

**Performance Goals:** measure combined usage, not a new latency SLA; backup integrity takes precedence over speed.

**Constraints:** no secret/private artifacts in Git, no historical dependency overwrite, no destructive restore, no automatic inference/download in CI.

**Scale/Scope:** one owner, private local release; no hosted distribution.

## Constitution Check

Local private backups, preserved originals, no cloud/automatic downloads; evidence distinguishes fake/manual; explicit spec and dedicated dependency review; reproducible tests and staged privacy checks. No exception. Native acceptance remains a release gate.

## Project Structure

Add `backend/backup.py`, `scripts/backup_incanta.py`, `scripts/restore_incanta.py`, `tests/test_backup_restore.py`, `tests/test_mvp_journey.py`, `docs/MVP_ACCEPTANCE.md`, `docs/RUNTIME_COMPATIBILITY.md`; update SETUP/OPERATIONS/ARCHITECTURE/TESTING and scoped requirements files. Keep `requirements.txt` historical; add reviewed direct/runtime lock instructions separately if needed. Backup manifests are generated in ignored private storage, not a new shared JSON allowlist.

## Design and execution

See [research](research.md), [data model](data-model.md), [contracts/maintenance.md](contracts/maintenance.md) and [quickstart](quickstart.md). Acquire maintenance gate, stop new generation/job commits and drain/cancel owned work safely, then use sqlite3 Connection.backup() and copy referenced immutable assets to a temporary backup root. Create manifest/checksums; publish backup directory atomically only after validation. Release gate in finally; never infer consistency from copying an open DB file. Do not include weights by default; record their local dependency identity/checksum privately.

Restore refuses a running app target or nonempty destination. Validate full manifest, hashes, schema and resolved contained paths before writing; reject symlinks/traversal and oversized/unexpected entries. Stage in a sibling temporary directory, verify DB integrity/relations and referenced files, neutralize old operational claims/notification attempts, then atomically publish into empty destination. Never execute backup content or modify source; partial directories remain clearly incomplete and can be removed only as owned temporary artifacts.

Dependency review records selected versions/licensing/native build switches and clean installation instructions; it does not introduce native inference into CI. Native acceptance records model/workflow hashes, OS/hardware, timing/peak memory, face/character owner verdict and explicit failure recovery. Existing private transcripts/references stay local. Release notes link individual verification records and unresolved issues. Create reviewed PRs and tag only after gates pass; no automatic merge or tag as part of planning.

## Complexity Tracking

Consistent multi-file backup needs a short maintenance gate and manifest; copying unrelated directories is unsafe. No encryption/key-management system or cloud backup is introduced; local backup confidentiality depends on the owner's local storage controls and explicit handling.
