# Isolated Acceptance Quickstart

1. Build `target/debug/rtk` in this worktree.
2. Use a disposable directory as `CODEX_HOME` for each test process.
3. Seed `hooks.json` with an unrelated safety hook.
4. Run global Codex init twice; require unchanged safety hook and one RTK entry
   last.
5. Pipe supported, unsupported, malformed, non-shell, and failure payloads to
   `rtk hook codex`; inspect stdout and status. A rewrite must contain
   `hookSpecificOutput.permissionDecision: "allow"` with `updatedInput` and no
   `permissionDecisionReason`; this is Codex wire compatibility, not approval.
6. Generate the five corpus outputs named in `spec.md`; capture combined stdout
   and stderr byte counts. Sort `100 × (raw-filtered)/raw` and require the third
   value ≥30%, while retaining status, failure identity, paths, counts, and
   recovery markers.
7. Uninstall; require only owned entries/files to disappear.
8. Delete the disposable directory; never use the real Codex home.
