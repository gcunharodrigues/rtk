# Tasks: Native Codex Hook

**Input**: Design artifacts in `specs/001-codex-native-hook/`

## Phase 1: Specification foundation

- [x] T001 Define approved requirements, constitution, contract, research, data model, and isolated quickstart in `specs/001-codex-native-hook/`
- [x] T002 Review `checklists/integration.md`; correct every unresolved requirement-quality gap before production

## Phase 2: User Story 1 — Transparent optimization (P1)

**Independent test**: supported Bash commands rewrite once; every passthrough class emits nothing and succeeds.

- [ ] T003 [US1] Add failing Codex CLI and payload contract tests in `src/main.rs` and `src/hooks/hook_cmd.rs`
- [ ] T004 [US1] Implement minimal shared-decision Codex processor in `src/hooks/hook_cmd.rs` and dispatch in `src/main.rs`
- [ ] T005 [US1] Run focused hook tests and commit the independently working processor

## Phase 3: User Story 2 — Safe configuration (P2)

**Independent test**: temporary config survives install twice/show/uninstall with unrelated hooks unchanged.

- [ ] T006 [US2] Add failing lifecycle tests in `src/hooks/init.rs`
- [ ] T007 [US2] Implement global and hook-only install, show, and narrow uninstall in `src/hooks/init.rs` and `src/hooks/constants.rs`
- [ ] T008 [US2] Update `hooks/codex/README.md`, run focused lifecycle tests, and commit

## Phase 4: User Story 3 — Measured savings (P3)

**Independent test**: disposable corpus meets semantic, median reduction, and latency gates.

- [ ] T009 [US3] Build the local binary and execute `quickstart.md` against a disposable Codex home
- [ ] T010 [US3] Record corpus inputs, byte results, semantic checks, and hook latency in `acceptance.md`

## Phase 5: Convergence and review

- [x] T011 Run specification analysis and append any discovered work
- [ ] T012 Run Documentation Impact Classification through `okf-maintain`
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
