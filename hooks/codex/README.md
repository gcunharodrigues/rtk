# Codex CLI Hooks

RTK can rewrite supported shell commands before Codex runs them. Codex keeps
approval decisions; RTK only returns a replacement command.

## Install

Use a disposable `CODEX_HOME` when testing. If `CODEX_HOME` is unset, RTK uses
`~/.codex/`.

```bash
rtk init -g --codex
```

Global install writes:

- `hooks.json` with one final `PreToolUse` entry for matcher `Bash`;
- `AGENTS.md` and `RTK.md` with RTK awareness.

The installed command is `rtk hook codex` with a 5-second timeout. Existing
hooks stay in their order. Re-running install is safe.

To install only the hook:

```bash
rtk init -g --codex --hook-only
```

Local `rtk init --codex` remains awareness-only and writes project `AGENTS.md`
and `RTK.md`.

## Verify and trust

```bash
rtk init --show --codex
```

Restart Codex after installation. If Codex asks for hook trust, review and
approve the exact `rtk hook codex` command. RTK does not set Codex permission
decisions.

## Passthrough behavior

Unsupported, empty, malformed, unsafe, already-prefixed, or disabled commands
produce no hook output and continue under Codex's original approval policy.
Malformed hook input and internal hook failures also fail open.

## Rollback

```bash
rtk init -g --codex --uninstall
```

Uninstall removes only exact `rtk hook codex` entries and RTK awareness it
installed. Mixed user hook groups remain. Before a changed `hooks.json` is
written, RTK saves `hooks.json.bak`; restore that backup manually if needed.

Malformed JSON or a concurrent change aborts the configuration write without
changing `hooks.json`. `--dry-run` reports changes without writing files.
