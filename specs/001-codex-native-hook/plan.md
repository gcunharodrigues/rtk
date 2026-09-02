# Implementation Plan: Native Codex Hook

**Branch**: `codex/rtk-codex-hook` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

## Summary

Add `rtk hook codex`, sharing Claude's command decision path but emitting a
Codex response without permission decisions. Extend global Codex init to merge
an RTK `PreToolUse` entry last in `$CODEX_HOME/hooks.json`; keep local init
instruction-only. Show, uninstall, docs, and a disposable lab cover lifecycle.

## Technical Context

**Language/Version**: Rust 2021, repository toolchain

**Dependencies**: Existing `clap`, `serde_json`, `anyhow`; none added

**Storage**: `$CODEX_HOME/hooks.json`, `AGENTS.md`, `RTK.md`

**Testing**: Rust tests; `cargo fmt`, `cargo clippy`, `cargo test`

**Target**: Codex CLI 0.146.0 on macOS; portable filesystem logic

**Project**: Single binary CLI

**Performance**: Hook processing under 10 ms on the acceptance machine

**Constraints**: Fail open; stdin ≤1 MiB; no async/network; never auto-approve

**Scope**: One hook command and existing Codex lifecycle surfaces

## Constitution Check

Pre-design PASS: shared registry; fail-open behavior; host-owned permissions;
tests before behavior; no dependency, network, production install, push, or
remote fork.

Post-design PASS: contract, data model, and quickstart preserve all principles.

## Brownfield Preflight

- Target: `/Users/guicr/.agents-worktrees/rtk-codex-hook`.
- Upstream base: `9a695d11b07ddb6378e9d74c3fa44403d48910ef` (`develop`).
- Governance: constitution v1.0.0 at commit `ef5a78f`.
- Initial state: clean production tree; only feature specs and generated,
  untracked `.agents/` copies existed.
- Caller: `src/main.rs`; processor: `src/hooks/hook_cmd.rs`.
- Consumers: Codex `PreToolUse`, init/show/uninstall, README, module tests.
- Invariants: fail open; centralized registry; preserve unrelated JSON; final
  pre-write snapshot verification; atomic configuration writes. `hooks.json`
  has no cooperative lock or compare-and-swap, so writers after that check are
  outside this protection.
- Baseline: `cargo test hook_cmd --lib` is inapplicable because RTK has no
  library target. Correct focused command: `cargo test hook_cmd`.
- Migration/UI: none.
- Risks: wrong wire shape, permission escalation, hook ordering, malformed JSON
  loss, overbroad uninstall, or an uncooperative writer after final snapshot
  verification.
- Rollback: `rtk init -g --codex --uninstall` or revert feature commits;
  existing config receives a `.bak` before write.

## Project Structure

```text
src/main.rs                  # CLI surface and dispatch
src/hooks/hook_cmd.rs        # Codex payload processing
src/hooks/init.rs            # install/show/uninstall lifecycle
src/hooks/constants.rs       # RTK-owned hook identity
hooks/codex/README.md        # operator documentation
specs/001-codex-native-hook/ # contract and acceptance evidence
```

**Decision**: Extend current modules and in-file tests; add no production module.

## Complexity Tracking

No constitution violations.
