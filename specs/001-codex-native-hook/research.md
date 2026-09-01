# Research: Native Codex Hook

## Decisions

### Share Claude's rewrite decision path

Codex and Claude supply `tool_name` plus `tool_input.command`. Share parsing,
safety classification, and the registry; vary only response serialization.
A second registry was rejected because it would drift.

### Return only `updatedInput`

Return `hookSpecificOutput.hookEventName="PreToolUse"` and
`hookSpecificOutput.updatedInput.command`. Never emit `permissionDecision` or
`permissionDecisionReason`; Codex remains authoritative. Copying Claude's
auto-allow response was rejected because it changes host approval.

### Global hook; compatible local awareness

`rtk init -g --codex` merges hook and awareness. `--hook-only` merges only the
hook. `rtk init --codex` remains local instruction-only.

### Append one owned entry last

Preserve unrelated hooks, remove RTK duplicates, append one canonical entry,
back up existing config, and write atomically. Earlier safety hooks run first.

### Disposable acceptance

Use temporary `CODEX_HOME`, the local binary, fixtures, and direct payloads.
No production config, remote fork, or push.

The local Codex 0.146.0 consumer accepts the nested updated string command.
Public OpenAI docs do not define the full wire contract, so a disposable canary
remains required.
