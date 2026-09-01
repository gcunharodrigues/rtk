# Data Model

## HookPayload

- `tool_name`: exactly `Bash`.
- `tool_input.command`: non-empty string.
- Other fields: opaque.

Invalid or unsupported payloads yield no response.

## HookResponse

- `hookSpecificOutput.hookEventName`: `PreToolUse`.
- `hookSpecificOutput.updatedInput`: original `tool_input` with only `command`
  replaced.
- Permission fields: forbidden.

## CodexHookEntry

- Matcher: `Bash`.
- Command: `rtk hook codex`.
- Timeout: 5 seconds.
- Ownership: exact canonical command match.

## Transitions

- Install: parse → preserve non-RTK entries → append RTK → backup → atomic write.
- Reinstall: same result, no duplicate.
- Uninstall: remove RTK entries; preserve all else; remove an empty owned event.
- Malformed JSON or a changed source snapshot: error, leaving the file unchanged.
