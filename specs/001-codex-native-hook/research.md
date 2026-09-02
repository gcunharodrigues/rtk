# Research: Native Codex Hook

## Decisions

### Share Claude's rewrite decision path

Codex and Claude supply `tool_name` plus `tool_input.command`. Share parsing,
safety classification, and the registry; vary only response serialization.
A second registry was rejected because it would drift.

### Return `updatedInput` with a protocol marker

Return `hookSpecificOutput.hookEventName="PreToolUse"` and
`hookSpecificOutput.updatedInput.command`, plus
`hookSpecificOutput.permissionDecision="allow"`. Codex CLI 0.151.0 rejects an
`updatedInput` response without that marker. It is required by the wire
parser, not an approval: Codex remains authoritative for approval and sandbox
policy. Never emit `permissionDecisionReason` or copy Claude's permission
rules.

### Global hook; compatible local awareness

`rtk init -g --codex` merges hook and awareness. `--hook-only` merges only the
hook. `rtk init --codex` remains local instruction-only.

### Append one owned entry last

Preserve unrelated hooks, remove RTK duplicates, append one canonical `Bash`
entry running `rtk hook codex`, back up existing config, verify the read
snapshot at final pre-write verification, and write atomically. Earlier safety
hooks run first. `hooks.json` has no cooperative lock or
compare-and-swap; an uncooperative writer after verification is outside this
protection.

### Disposable acceptance

Use temporary `CODEX_HOME`, the local binary, fixtures, and direct payloads.
No production config, remote fork, or push.

The Codex `rust-v0.151.0` source parser requires the nested `allow` marker with
an updated command and rejects the otherwise valid envelope without it. Public
OpenAI docs do not define the full wire contract, so the source canary remains
the compatibility evidence.
