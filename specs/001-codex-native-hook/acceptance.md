# Acceptance Evidence

**Production candidate**: `e47d588c9e4dfa20df32d08fe54676d684fa6c59`

The only changes after this production SHA are the verifier rebind and this
feature evidence. The verifier rebuilds the production SHA instead of trusting
`HEAD`.

## Hook and lifecycle

- Supported `Bash` payload rewrote `git status` to `rtk git status`, preserved
  sibling input fields, and emitted no permission fields.
- Non-Bash, unsafe substitution, and >1 MiB payloads exited 0 with 0 stdout bytes.
- Lifecycle tests using two global installs proved that seeded unrelated
  `PreToolUse`, `Stop`, and arbitrary root data retained JSON values; unrelated
  hook groups and entries retained their relative order. Exactly one RTK hook
  remained last with timeout 5. Whitespace, escaping, and object-key order may
  be canonically reserialized; the pre-write `hooks.json.bak` retained the prior
  bytes for textual rollback.
- Hook-only created only `hooks.json` and printed no awareness path.
- Show reported both surfaces. Uninstall retained all seeded safety hooks and
  removed only RTK hook/awareness.
- A source changed before final pre-write snapshot verification aborted without
  replacing `hooks.json`; replacement after that check is atomic. `hooks.json`
  has no cooperative lock or compare-and-swap, so an uncooperative writer after
  the check is outside this protection.
- Codex install/uninstall reject symlinked `hooks.json.bak` destinations before
  backup, and dangling `hooks.json` symlinks fail without replacing the link;
  valid configuration symlinks remain supported.
- The real Codex home was never used.
- A synthetic Claude `Bash(git status)` deny did not suppress the Codex rewrite.
  `--show --codex` reports healthy only for one canonical final entry; malformed,
  duplicate, disabled, wrong-matcher, wrong-timeout, and wrong-position cases fail.

## Registry coverage

The Codex adapter uses permission-neutral `decide_from_verdict(Default) →
get_rewritten → rewrite_command → RULES`. The exhaustive Codex payload corpus
asserted set equality and rewrote all **87/87 unique RTK targets exactly once**,
while emitting no permission fields; Codex owns approval. `cargo test hook_cmd`
passed all 118 hook tests. No Codex-specific registry exists.

## Recorded production checks

These are recorded commands and results. Every RED observation occurred in an
uncommitted worker state before its logical GREEN commit. No immutable RED tree
or transcript was retained, so the historical commands and results cannot be
rerun from the named GREEN commits. The constitution requires observed RGR, not
a broken commit. Only the fixed-SHA corpus and latency methods below are
reproducible measurements.

| Change | RED | GREEN / refactor |
|---|---|---|
| Initial processor (`6e2e157`) | `cargo test codex -- --nocapture` — compile failure: missing `run_codex_inner` / `HookCommands::Codex`. | `cargo test codex -- --nocapture`; then `cargo fmt --all --check`, `cargo clippy --all-targets`, `cargo test hook_cmd`, and `cargo test --all`. Recorded: 13 Codex tests, 115 hook tests, Clippy, format, and 2,933 repository tests passed. |
| Lifecycle (`cb3a5ca`) | `cargo test codex_hook -- --nocapture` — missing `CODEX_HOOK_COMMAND` / merge. | `cargo test codex_hook -- --nocapture` — 9 lifecycle tests; `cargo test hooks::init::tests -- --nocapture` — 193 init tests. |
| Latency refactor (`e18d41c`) | The latency runner below, built from `cb3a5ca8c96d22d6cbb6bf65b4aa51243ff763e5`: 16.247 ms median. | The same runner, built from `e18d41c02c3cb7d02007a23ff2ac023444930df4`: 7.275 ms median and 8.047 ms p95; `cargo test test_candidate_prefilter_preserves_last_match -- --nocapture`. |
| Permission and status (`9838e31`) | Claude deny suppressed Codex rewrite; malformed hook reported healthy. | `cargo test test_codex_rewrite_ignores_claude_deny_rules -- --nocapture`; `cargo test test_codex_hook_status_requires_one_canonical_final_entry -- --nocapture`. Recorded fixed-candidate evidence: 23 Codex tests, Clippy, format, and diff checks passed. |
| Alternate forms (`c89508a`) | `cargo test test_rewrite_supported_alternate_forms -- --nocapture`; `cargo test test_codex_rewrites_supported_alternate_forms -- --nocapture` — expected alternate forms did not rewrite. | Both tests passed; that candidate's focused check passed 24 Codex, 394 registry, and 118 hook tests. |
| Group preservation (`02dc193`) | Metadata-only and pre-existing-empty-container tests failed. | 14 focused lifecycle tests passed; the fixed-candidate check below passed 28 Codex, 394 registry, 118 hook, and 199 init tests. |
| Empty-container round trip (`dcd395d`) | Install followed by uninstall removed a pre-existing empty `PreToolUse` array. | The canonical test and a dedicated install/uninstall round-trip test passed; the fixed-candidate check below passed 29 Codex, 394 registry, 118 hook, and 200 init tests. |
| Symlink-safe backup/write (`e47d588`) | `cargo test symlink -- --nocapture` — the three new regressions all returned `Ok(true)` instead of rejecting symlink targets. | `cargo test symlink -- --nocapture` passed 7 tests; the fixed-candidate check below passed 32 Codex, 394 registry, 118 hook, and 203 init tests; Clippy, format, and diff checks passed. |

`git diff --check` was the recorded diff check. The final full-suite task remains
unchecked in [tasks.md](tasks.md); no final-suite result is claimed here.

## Byte-savings corpus

**Machine**: `Guilhermes-Air`; `macOS-26.6.2-arm64-arm-64bit-Mach-O`.

Build `e47d588c9e4dfa20df32d08fe54676d684fa6c59` with `cargo build --release --offline`.
Each command ran with `subprocess.run(..., capture_output=True)`; bytes are
`stdout + stderr`, and the exit status is retained, including expected failure.
The committed fixture is `fixtures/failing-rust/`. The method cleans distinct
raw and filtered `CARGO_TARGET_DIR` paths before measuring.

| Case | Raw command | Filtered command | Raw / filtered bytes | Reduction | Status |
|---|---|---|---:|---:|---:|
| Git log | fixed-range `git log --stat --oneline` | isolated production build: `rtk git log --stat --oneline` | 7,138 / 7,138 | 0.0% | 0 |
| Git diff | fixed-range `git diff` | isolated production build: `rtk git diff` | 137,646 / 35,900 | 73.9% | 0 |
| File listing | `find src docs hooks specs -type f` | isolated production build: `rtk find src docs hooks specs -type f` | 7,160 / 1,249 | 82.6% | 0 |
| Text search | `rg -n test src` | isolated production build: `rtk rg -n test src` | 601,103 / 12,864 | 97.9% | 0 |
| Failing Rust test | isolated fixture `cargo test --verbose` | isolated production build: `rtk cargo test --verbose` | 2,315 / 503 | 78.3% | 101 |

The executable comparator is:

```sh
python3 specs/001-codex-native-hook/verify_acceptance.py
```

It reconstructs `e47d588` with `git archive`, builds that tree offline, and runs
the corpus there. It returned `ok: true` and **78.3% median reduction**. Its
case-specific assertions proved: equal commit count and log output; every
changed diff path plus exact file/insertion/deletion totals; exact file and
search counts; representative paths; truncation markers; readable isolated
recovery files containing hidden paths;
and failing-test identity, count, and status 101. Adversarial self-checks reject
false diff totals and irrelevant recovery files. The symlink safety self-test
returned `symlinked_corpus_rejected_without_touching_sentinel: true`: it rejected
a symlinked corpus directory without changing its external sentinel. Every raw
case exceeded 1 KiB.
The values are machine-specific; the semantic assertions and 30% median gate
are the acceptance criteria.

## Latency

The release command was `cargo build --release`. The hook payload was JSON
`Bash` / `git status`; the runner used five warmups, then 200 subprocesses,
`perf_counter_ns`, `PATH=/usr/bin:/bin:/usr/sbin:/sbin`, and
`RTK_HOOK_AUDIT=0`.

```python
import json, statistics, subprocess, time

payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}}).encode()
env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "RTK_HOOK_AUDIT": "0"}
command = ["./target/release/rtk", "hook", "codex"]

def run():
    started = time.perf_counter_ns()
    result = subprocess.run(command, input=payload, capture_output=True, env=env)
    assert result.returncode == 0
    return (time.perf_counter_ns() - started) / 1_000_000

for _ in range(5):
    run()
samples = sorted(run() for _ in range(200))
print(statistics.median(samples), samples[189], samples[-1])
```

For `e47d588c9e4dfa20df32d08fe54676d684fa6c59`, the recorded median was
**6.887 ms**, p95 **7.576 ms**, maximum **8.205 ms**. The timing data does not
establish the cause of the maximum. The acceptance target is median < 10 ms; no
p95 or maximum target is claimed.

## Fixed-candidate Focused Check

- Candidate: `e47d588c9e4dfa20df32d08fe54676d684fa6c59`.
- Scope: `src/main.rs`, `src/hooks/{hook_cmd,init,constants,permissions}.rs`,
  `src/discover/{registry,rules}.rs`, and `hooks/codex/README.md`.
- Consumers: Codex `PreToolUse`, CLI parsing, init/show/uninstall, shared registry.
- Command: `cargo test codex && cargo test discover::registry::tests && cargo test hooks::hook_cmd::tests && cargo test hooks::init::tests`.
- Result: PASS — 32 Codex, 394 registry, 118 hook, and 203 init tests.
- Individual test execution elapsed: 0.09, 0.34, 0.09, and 0.06 seconds respectively;
  the slowest focused step was the registry suite at 0.34 seconds.
- Focused target: 60 seconds; met.

## Independent Review and Final Gate

- Closed review SHA: `d595565342ee49eaa404a9dff356e431744e7e3c`.
- Independent review: PASS.
- Unchanged-candidate command: `/usr/bin/time -p sh -c 'cargo fmt --all --check && cargo clippy --all-targets -- -D warnings && cargo test --all'`.
- Result: PASS — 2,954 unit tests and 83 integration tests passed (3,037 total),
  8 ignored, 0 failed; format and Clippy passed.
- `/usr/bin/time -p` reported `real 21.43`. The slowest test target was
  `copilot_selfheal_test` at 2.33 seconds.
- This section and the matching task state are evidence-only documentation
  written after the gate; production remains
  `e47d588c9e4dfa20df32d08fe54676d684fa6c59`.

## Documentation Impact Classification

Classification: `documentation`. The owning Codex README and feature acceptance
record now describe installation, trust, restart, passthrough, rollback,
measured savings, and latency. No map or ADR was added because this is a
reversible local fork feature whose durable behavior is already discoverable
from those repository-local surfaces and commits.
