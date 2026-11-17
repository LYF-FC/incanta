# Implementation Plan: Celeste conversations and controlled memory

**Branch**: `codex/002-companion-conversations` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Status:** planned only. Dependencies: [001](../001-reliable-local-chat/verification.md). No implementation from this planning pass.

## Summary

Retain Flask/plain JavaScript and lazy local inference. Replace process-global conversation ownership with explicit conversation IDs and transactional per-conversation state. Use Python's standard-library SQLite for shared canonical facts, durable revisions and exactly-once local request commits. Make legacy JSON import explicit and non-destructive. Implement synthetic acceptance before native checks.

## Technical Context

**Language/Version:** Python 3.11/3.13; plain browser JavaScript.

**Primary Dependencies:** existing Flask, standard-library sqlite3; optional existing llama-cpp-python. No database server/new frontend framework.

**Storage:** owner-configured local SQLite file; foreign keys enabled on every connection; short transactions, one connection per operation, no connection sharing between threads. Start with rollback journal and full synchronous writes; WAL is deferred until measured need.

**Testing:** unittest/Flask client, Node tests, fake inference and temporary DB; subprocess restart and crash/rollback tests.

**Target Platform:** local Mac M2/16 GB; model-free CI on Linux.

**Project Type:** existing web app.

**Performance Goals:** synthetic selection/status/reload under two seconds, excluding startup; native dialogue timing measured, not promised.

**Constraints:** no private fixtures/logging/cloud, one process, no DB transaction held during inference; bounded context; settings/fact changes invalidate pending results.

**Scale/Scope:** one owner, multiple conversations, one foreground generation at a time.

## Constitution Check

Privacy: local DB and synthetic tests only. Evidence: all new behavior remains planned. Specification first: FR/SC-to-task mapping below. Reproducibility: fake tests, explicit native gate. Recoverability: owner-confirmed import with preserved originals and backup. All design gates pass; no constitution exception. Recheck after implementation.

## Project Structure

`backend/conversation_store.py`, `backend/conversation_service.py`, `backend/fact_store.py`, `backend/legacy_import.py`, `backend/migrations/001_companion.sql`; modify `backend/config.py`, `backend/chat_engine.py`, `backend/llm_interface.py`, `frontend_app.py`, `frontend/app.js`, `frontend/index.html`, `frontend/style.css`; add `frontend/memory_controls.js`. Test files: `tests/test_conversations.py`, `tests/test_facts.py`, `tests/test_legacy_import.py`, `tests/conversations.test.js`. Documentation stays in this directory plus SETUP/ARCHITECTURE/ASSETS.

## Design and execution

Phase 0 decisions are in [research.md](research.md). Phase 1 schema, transitions and contracts are in [data-model.md](data-model.md) and [contracts/http.md](contracts/http.md). Runtime DB location is configured by `INCANTA_DATABASE_PATH`, anchored like existing settings; missing storage never triggers an empty replacement of an existing corrupt file.

Acquire the shared process generation lock, capture settings/context revision and permitted facts, release DB read transaction, generate, then begin a write transaction and recheck revisions. Commit one turn and all conversation state together or return `context_changed`. Use a per-conversation client request UUID with a unique constraint; same ID/content replays the committed result, different content conflicts. Facts/revisions/grants mutate in one transaction, bumping recipient context revisions; capture source and fact IDs, not a copied fact string as an authoritative cache.

Build a bounded prompt with an explicit system-role settings block, attributed memories, recent committed turns and current user input; reserve model output space, trim oldest turns first, and reject an irreducibly oversized configuration. Eliminate hard-coded Celeste personality instructions and the generated-sibling heuristic. Do not describe prompt instructions as a security boundary.

Legacy import previews document shape/counts locally, makes an explicit consistent backup, stores original source bytes as an ignored local preservation artifact for unknown fields, and commits imported turns/import hash once. It does not auto-scan private folders. Use the store interfaces in later image/scheduler features; do not introduce those workers here.

## Complexity Tracking

SQLite is justified by cross-conversation fact relationships and atomic revision checks; independent JSON copies cannot reliably propagate correction/deletion. No server framework rewrite, external database, vector index or automatic migration is needed.
