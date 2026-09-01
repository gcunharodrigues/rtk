<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Added principles: faithful compression; never block; hook security; test-first; minimal integration
- Added sections: Runtime Constraints; Development Workflow
- Removed sections: none
- Follow-up TODOs: none
-->
# RTK Constitution

## Core Principles

### I. Faithful Compression
Filtered output MUST preserve requested detail, exit status, failure identity, recovery hints, and the
semantics needed for an agent to act correctly. Explicit verbose or diagnostic flags MUST take
precedence over token reduction. Byte savings never justify silent loss of consequential signal.

### II. Never Block
Unsupported input, malformed hook payloads, unavailable dependencies, and filter failures MUST pass
through unchanged. Hooks MUST exit successfully on their own error paths and MUST NOT prevent the
underlying command from running.

### III. Host Permissions Remain Authoritative
An integration MAY rewrite command input but MUST NOT broaden, bypass, or silently approve the host
agent's permission decision. Command mutation MUST occur only after existing safety gates have had an
opportunity to inspect the original command.

### IV. Test First
Behavior changes MUST begin with a failing test at the public seam. Tests MUST cover normal input,
passthrough, malformed input, boundary limits, and permission-sensitive behavior before production
code is accepted.

### V. Minimal Native Integration
New agent support MUST reuse the existing registry, parser, audit, init, merge, backup, and uninstall
patterns. A host-specific adapter MUST contain only the protocol differences that cannot be shared.

## Runtime Constraints

RTK remains a single-threaded Rust CLI with no async runtime or network call on the hook path. Hook
stdin is bounded to 1 MiB. The target startup time is below 10 ms. Production code uses contextual
`anyhow::Result` errors and no `unwrap()`. Telemetry, global installation, and publication are outside
an integration's default authority.

## Development Workflow

Every production task uses Red-Green-Refactor, one logical commit, and a focused check. The integrated
candidate then passes formatting, Clippy, the complete Rust test suite, documentation impact
classification, independent code review, and one unchanged-candidate final gate. Source writes occur
only in an isolated worktree; unrelated upstream code is preserved.

## Governance

This constitution governs feature work in this fork. Amendments require an explicit rationale, impact
report, and semantic version change: MAJOR for incompatible principle changes, MINOR for new principles
or materially expanded obligations, PATCH for clarification. Reviews MUST cite any exception; an
unjustified exception blocks acceptance. `CLAUDE.md`, `CONTRIBUTING.md`, and `.claude/rules/` provide
runtime guidance consistent with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-09-01 | **Last Amended**: 2026-09-01
