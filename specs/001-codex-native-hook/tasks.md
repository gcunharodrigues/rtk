# Tasks: Native Codex Hook

**Input**: Design artifacts in `specs/001-codex-native-hook/`

## Phase 1: Specification foundation

- [x] T001 Define approved requirements, constitution, contract, research, data model, and isolated quickstart in `specs/001-codex-native-hook/`
- [x] T002 Review `checklists/integration.md`; correct every unresolved requirement-quality gap before production

## Phase 2: User Story 1 — Transparent optimization (P1)

**Independent test**: supported Bash commands rewrite once; every passthrough class emits nothing and succeeds.

- [x] T003 [US1] Add failing Codex CLI and payload contract tests in `src/main.rs` and `src/hooks/hook_cmd.rs`
- [x] T004 [US1] Implement minimal shared-decision Codex processor in `src/hooks/hook_cmd.rs` and dispatch in `src/main.rs`
- [x] T005 [US1] Run focused hook tests and commit the independently working processor

## Phase 3: User Story 2 — Safe configuration (P2)

**Independent test**: temporary config survives install twice/show/uninstall with unrelated hooks unchanged.

- [x] T006 [US2] Add failing lifecycle tests in `src/hooks/init.rs`
- [x] T007 [US2] Implement global and hook-only install, show, and narrow uninstall in `src/hooks/init.rs` and `src/hooks/constants.rs`
- [x] T008 [US2] Update `hooks/codex/README.md`, run focused lifecycle tests, and commit

## Phase 4: User Story 3 — Measured savings (P3)

**Independent test**: disposable corpus meets semantic, median reduction, and latency gates.

- [x] T009 [US3] Build the local binary and execute `quickstart.md` against a disposable Codex home
- [x] T010 [US3] Record corpus inputs, byte results, semantic checks, and hook latency in `acceptance.md`

## Phase 5: Convergence and review

- [x] T011 Run specification analysis and append any discovered work
- [x] T012 Run Documentation Impact Classification through `okf-maintain`
- [ ] T013 Obtain independent read-only code review of the fixed candidate
- [ ] T014 Run the unchanged-candidate gate: `cargo fmt --all --check`, `cargo clippy --all-targets`, `cargo test --all`

## Dependencies

`T001 → T002 → T003–T005 → T006–T008 → T009–T010 → T011–T014`.
Production tasks are serial because they overlap the CLI and hook lifecycle.

## Execution Waves

- Wave 0: T001–T002 (requirements gate).
- Wave 1: T003–T005 (processor; one logical commit).
- Wave 2: T006–T008 (configuration lifecycle; one logical commit).
- Wave 3: T009–T010 (acceptance evidence; depends on both production commits).
- Wave 4: T011–T014 (closed-candidate checks; strictly serial).

## Strategy

Ship P1 first, validate it independently, then add reversible configuration,
then accept only with measured savings and semantic evidence.

## Execution Evidence

- `6e2e157 feat(hook): add native Codex command rewrite` — RED: missing
  `run_codex_inner`/`HookCommands::Codex`; GREEN: 13 Codex tests, 115 hook
  tests, Clippy, format, and 2,933 repository tests passed.
- `cb3a5ca feat(init): install native Codex hook` — RED: missing
  `CODEX_HOOK_COMMAND`/merge; GREEN: 9 lifecycle tests, 193 init tests,
  Clippy, format, and disposable CLI smoke passed.
- `e18d41c perf(registry): reduce hook startup latency` — RED: 16.247 ms
  release median; GREEN: 7.275 ms median, 8.047 ms p95, 393 registry tests,
  115 hook tests, Clippy, and format passed.
- `7e18320 test(hook): cover every registry target` — 87/87 unique
  registry targets exercised through the Codex payload path; 116 hook tests,
  Clippy, format, and diff checks passed.
- `3828682` and `d24150d` align every canonical Codex hook surface and contract
  with native installation, Codex-owned permissions, and the detectable
  concurrent-change boundary.
- Evidence paths `specs/001-codex-native-hook/{acceptance.md,tasks.md}` bind
  to production SHA `d24150d8edada0f0241e2f640558c59978d9f7fb`.

## Phase 6: Convergence

- [x] T015 Optimize lazy registry matching and retain complete rewrite behavior so release hook startup meets the below-10-ms target per SC-005 (partial)

## Phase 7: Review remediation

- [x] T016 Add an exhaustive Codex hook corpus test with one valid representative for every unique RTK registry target, and record its results per SC-001
- [x] T017 Clarify the detectable concurrent-change boundary and update every canonical Codex hook document identified by review
