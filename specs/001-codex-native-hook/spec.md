# Feature Specification: Native Codex Hook

**Feature Branch**: `codex/rtk-codex-hook`

**Created**: 2026-09-01

**Status**: Approved

**Input**: Add a native Codex hook to RTK, matching Claude command coverage while preserving Codex permissions, and validate it in an isolated environment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Transparent command optimization (Priority: P1)

A Codex user runs ordinary shell commands and receives RTK-compressed output without manually adding an RTK prefix.

**Why this priority**: Transparent adoption is the feature's primary token-saving value.

**Independent Test**: Feed supported and unsupported shell commands through the hook and verify only supported commands are rewritten.

**Acceptance Scenarios**:

1. **Given** a supported shell command, **When** Codex invokes it, **Then** the command is rewritten through RTK before execution.
2. **Given** an unsupported, malformed, or already rewritten command, **When** the hook handles it, **Then** execution proceeds unchanged.

---

### User Story 2 - Safe Codex configuration (Priority: P2)

A Codex user can install, inspect, and remove the integration without losing existing hooks or instructions.

**Why this priority**: Global configuration must be reversible and preserve the source observed through final pre-write verification.

**Independent Test**: Exercise install, repeated install, show, dry-run, and uninstall against a temporary Codex home containing unrelated hooks.

**Acceptance Scenarios**:

1. **Given** existing Codex hooks, **When** RTK is installed, **Then** existing entries remain byte-equivalent and RTK is appended last.
2. **Given** an installed RTK hook, **When** uninstall runs, **Then** only RTK-owned entries and awareness files are removed.

---

### User Story 3 - Evidence-backed token savings (Priority: P3)

A maintainer can determine whether the Codex integration saves meaningful shell-output bytes without hiding consequential information.

**Why this priority**: Adoption is justified only by measured savings with semantic safety.

**Independent Test**: Compare raw and filtered outputs across a disposable representative command corpus.

**Acceptance Scenarios**:

1. **Given** representative noisy outputs above 1 KiB, **When** raw and filtered results are compared, **Then** median byte reduction is at least 30%.
2. **Given** a failing or detailed command, **When** output is filtered, **Then** exit status, failure identity, paths, counts, and recovery markers remain available.

### Edge Cases

- Hook stdin exceeds 1 MiB, contains a BOM, invalid JSON, no command, or a non-shell tool.
- Commands contain heredocs, substitutions, redirections, compound operators, explicit detail flags, or `RTK_DISABLED=1`.
- Existing hook configuration is empty, malformed, duplicated, reordered, or changed before final pre-write verification.
- RTK is absent or the hook process fails.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a Codex hook processor using the same supported-command registry as Claude.
- **FR-002**: The processor MUST rewrite only Codex shell commands with non-empty textual command input.
- **FR-003**: The processor MUST preserve Codex-native approval behavior, MUST NOT auto-approve rewritten commands, and MUST NOT emit `permissionDecision` fields.
- **FR-004**: Unsupported or invalid inputs and internal failures MUST pass through without blocking execution.
- **FR-005**: Global Codex initialization MUST merge one final `PreToolUse` entry with matcher `Bash` and command `rtk hook codex`, atomically and idempotently.
- **FR-006**: Hook-only initialization MUST avoid adding RTK instructions to the model context.
- **FR-007**: Show and uninstall MUST identify or remove only RTK-owned configuration.
- **FR-008**: Existing local Codex instruction-only initialization MUST remain compatible.
- **FR-009**: The integration MUST document restart, hook trust, rollback, and passthrough behavior.
- **FR-010**: A configuration write MUST abort without changing the target when final pre-write snapshot verification finds that the source differs. After that verification, it MUST atomically replace the target. An uncooperative writer after the check is outside this protection because `hooks.json` has no cooperative lock or compare-and-swap.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every supported command in the acceptance corpus is rewritten once; every unsupported command is unchanged.
- **SC-002**: Existing hook entries survive install/uninstall with no semantic change.
- **SC-003**: Median byte reduction is at least 30% for representative raw outputs above 1 KiB.
- **SC-004**: No tested command loses exit status, failure identity, relevant paths, counts, or truncation recovery markers.
- **SC-005**: Hook processing remains below the project's 10 ms startup target on the test machine.

### Acceptance Corpus

- Rewrite coverage MUST enumerate every command family returned by the existing RTK registry and use one safe representative command per family; execution is not required for mutating or unavailable tools.
- Savings measurement MUST use five disposable outputs above 1 KiB: Git log, Git diff, recursive file listing, repeated text search, and a failing Rust test fixture.
- Per-case byte reduction is `100 × (raw_bytes - filtered_bytes) / raw_bytes`, using stdout and stderr together. The acceptance value is the third value after sorting the five reductions numerically.
- Semantic checks compare the raw and filtered cases for exit status, failing test identity, relevant paths, total counts, and any truncation/recovery marker.

## Assumptions

- Codex 0.146.0 maps its shell tool to Claude-compatible `PreToolUse` input with `tool_name="Bash"` and `tool_input.command`.
- Codex accepts `hookSpecificOutput.updatedInput.command` and owns all permission decisions.
- The pilot uses the complete existing RTK registry; production installation is outside this feature.
- The fork remains local and private; no remote publication or upstream pull request is included.
