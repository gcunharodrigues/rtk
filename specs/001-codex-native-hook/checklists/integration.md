# Integration Requirements Checklist: Native Codex Hook

**Purpose**: Reviewer gate for contract, safety, lifecycle, and evidence quality

**Created**: 2026-09-01

**Feature**: [spec.md](../spec.md)

## Contract and safety

- [x] CHK001 Is the accepted Codex input/output wire shape explicit, including preserved fields? [Clarity, Spec §FR-001–FR-003]
- [x] CHK002 Is the required wire marker distinct from approval ownership, with the permission reason forbidden? [Safety, Spec §FR-003]
- [x] CHK003 Are malformed, unsupported, disabled, unsafe, and internal-failure passthrough cases complete? [Coverage, Spec §FR-004]
- [x] CHK004 Is the 1 MiB input boundary specified with fail-open behavior? [Edge Case, Spec §Edge Cases]

## Configuration lifecycle

- [x] CHK005 Are global, hook-only, and local modes distinguished without conflict? [Consistency, Spec §FR-005–FR-008]
- [x] CHK006 Is hook ordering objectively defined as one RTK-owned entry appended last? [Measurability, Spec §FR-005]
- [x] CHK007 Are malformed and concurrent configuration failure outcomes stated without risking user data? [Recovery, Spec §Edge Cases]
- [x] CHK008 Is uninstall ownership narrow enough to protect unrelated entries and files? [Safety, Spec §FR-007]

## Acceptance evidence

- [x] CHK009 Is the savings corpus threshold and median calculation measurable? [Acceptance, Spec §SC-003]
- [x] CHK010 Are all semantic details that compression must retain enumerated? [Completeness, Spec §SC-004]
- [x] CHK011 Is the latency measurement boundary defined as hook processing? [Clarity, Spec §SC-005]
- [x] CHK012 Does isolated validation explicitly exclude the real Codex home, publishing, and pushing? [Scope, Assumption]

## Notes

Reviewer-owned: `[x]` means only that the written requirement is sufficient.
