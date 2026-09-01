# Contract: Codex PreToolUse

## Input

```json
{"tool_name":"Bash","tool_input":{"command":"git status"}}
```

## Rewritten output

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","updatedInput":{"command":"rtk git status"}}}
```

No permission decision is allowed. Existing `tool_input` fields are preserved.

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
is 5 seconds. A detected concurrent change aborts the write without modifying
the target.
