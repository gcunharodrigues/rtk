# Contract: Codex PreToolUse

## Input

```json
{"tool_name":"Bash","tool_input":{"command":"git status"}}
```

## Rewritten output

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","updatedInput":{"command":"rtk git status"}}}
```

Codex CLI 0.151.0 requires the `permissionDecision: "allow"` wire marker when
`updatedInput` is returned. The marker makes the response compatible with the
Codex PreToolUse parser; it does not auto-approve the command or replace the
Codex executor's approval and sandbox decisions. `permissionDecisionReason` is
never emitted. Existing `tool_input` fields are preserved.

## Passthrough

Malformed JSON, non-`Bash` tools, empty/unsupported/already-prefixed commands,
unsafe shell syntax, disabled RTK, and internal failures exit successfully
without stdout. Codex keeps the original input and approval policy.

Input above 1 MiB follows the same successful, empty passthrough behavior.

## CLI

- `rtk init -g --codex`: hook and awareness.
- `rtk init -g --codex --hook-only`: hook only.
- `rtk init --codex`: local awareness only.
- `rtk init --show --codex`: report both owned surfaces.
- `rtk init -g --uninstall --codex`: remove only owned surfaces.

The installed hook matcher is `Bash`, command is `rtk hook codex`, and timeout
is 5 seconds. At final pre-write snapshot verification, a source difference
aborts without changing the target. After that verification, RTK atomically
replaces the target. `hooks.json` has no cooperative lock or compare-and-swap,
so an uncooperative writer after the check is outside this protection.
