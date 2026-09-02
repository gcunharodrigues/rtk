# Acceptance Evidence

**Production candidate**: `daae1bfff06e5bf0f67068372c4f6cf02d68d9dd`

## Hook and lifecycle

- Supported `Bash` payload rewrote `git status` to `rtk git status`, preserved
  sibling input fields, and emitted no permission fields.
- Non-Bash, unsafe substitution, and >1 MiB payloads exited 0 with 0 stdout bytes.
- Two global installs preserved seeded `PreToolUse`, `Stop`, and arbitrary root
  data; exactly one RTK hook remained last with timeout 5.
- Hook-only created only `hooks.json` and printed no awareness path.
- Show reported both surfaces. Uninstall retained all seeded safety hooks and
  removed only RTK hook/awareness.
- A source changed before final pre-write snapshot verification aborted without
  replacing `hooks.json`; replacement after that check is atomic. `hooks.json`
  has no cooperative lock or compare-and-swap, so an uncooperative writer after
  the check is outside this protection.
- The real Codex home was never used.
- A synthetic Claude `Bash(git status)` deny did not suppress the Codex rewrite.
  `--show --codex` reports healthy only for one canonical final entry; malformed,
  duplicate, disabled, wrong-matcher, wrong-timeout, and wrong-position cases fail.

## Registry coverage

The Codex adapter uses permission-neutral `decide_from_verdict(Default) →
get_rewritten → rewrite_command → RULES`. The exhaustive Codex payload corpus
asserted set equality and rewrote all **87/87 unique RTK targets exactly once**,
while emitting no permission fields; Codex owns approval. `cargo test hook_cmd`
passed all 116 hook tests. No Codex-specific registry exists.

## Recorded production checks

These are recorded commands and results, not a claim that a new checkout will
reproduce historical timings or test counts.

| Change | RED | GREEN / refactor |
|---|---|---|
| Initial processor (`6e2e157`) | `cargo test codex -- --nocapture` — compile failure: missing `run_codex_inner` / `HookCommands::Codex`. | `cargo test codex -- --nocapture`; then `cargo fmt --all --check`, `cargo clippy --all-targets`, `cargo test hook_cmd`, and `cargo test --all`. Recorded: 13 Codex tests, 115 hook tests, Clippy, format, and 2,933 repository tests passed. |
| Lifecycle (`cb3a5ca`) | `cargo test codex_hook -- --nocapture` — missing `CODEX_HOOK_COMMAND` / merge. | `cargo test codex_hook -- --nocapture` — 9 lifecycle tests; `cargo test hooks::init::tests -- --nocapture` — 193 init tests. |
| Latency refactor (`e18d41c`) | The latency runner below, built from `cb3a5ca8c96d22d6cbb6bf65b4aa51243ff763e5`: 16.247 ms median. | The same runner, built from `e18d41c02c3cb7d02007a23ff2ac023444930df4`: 7.275 ms median and 8.047 ms p95; `cargo test test_candidate_prefilter_preserves_last_match -- --nocapture`. |
| Permission and status (`9838e31`) | Claude deny suppressed Codex rewrite; malformed hook reported healthy. | `cargo test test_codex_rewrite_ignores_claude_deny_rules -- --nocapture`; `cargo test test_codex_hook_status_requires_one_canonical_final_entry -- --nocapture`. Recorded fixed-candidate evidence: 23 Codex tests, Clippy, format, and diff checks passed. |

`git diff --check` was the recorded diff check. The final full-suite task remains
unchecked in [tasks.md](tasks.md); no final-suite result is claimed here.

## Byte-savings corpus

**Machine**: `Guilhermes-Air`; `macOS-26.6.2-arm64-arm-64bit-Mach-O`.

Build the candidate with `cargo build --release`. Each command ran with
`subprocess.run(..., capture_output=True)`; bytes are `stdout + stderr`, and
the exit status is retained, including expected failure. The committed fixture
is `fixtures/failing-rust/`. Start both distinct `CARGO_TARGET_DIR` paths
empty so raw and filtered runs do not share build output.

| Case | Raw command | Filtered command | Raw / filtered bytes | Reduction | Status |
|---|---|---|---:|---:|---:|
| Git log | `git log --all --stat --oneline` | `./target/release/rtk git log --all --stat --oneline` | 469,993 / 469,993 | 0.0% | 0 |
| Git diff | `git diff 9cdf66f805adc7a710a4f517a2829fae96c49525..daae1bfff06e5bf0f67068372c4f6cf02d68d9dd` | `./target/release/rtk git diff 9cdf66f805adc7a710a4f517a2829fae96c49525..daae1bfff06e5bf0f67068372c4f6cf02d68d9dd` | 81,604 / 31,346 | 61.6% | 0 |
| File listing | `find . -type f` | `./target/release/rtk find . -type f` | 1,579,896 / 1,057 | 99.9% | 0 |
| Text search | `rg -n test src` | `./target/release/rtk rg -n test src` | 599,036 / 12,656 | 97.9% | 0 |
| Failing Rust test | `CARGO_TARGET_DIR=target/codex-corpus/raw cargo test --manifest-path specs/001-codex-native-hook/fixtures/failing-rust/Cargo.toml` | `CARGO_TARGET_DIR=target/codex-corpus/filtered ./target/release/rtk cargo test --manifest-path specs/001-codex-native-hook/fixtures/failing-rust/Cargo.toml` | 2,344 / 477 | 79.7% | 101 |

The failing case retained `preserves_failure_details`; `0 passed; 1 failed`.
Median: **79.7%**. The values are the recorded result for the named machine
and candidate, not a cross-machine byte-for-byte threshold.

```python
import os, subprocess

def measure(command, env=None):
    run = subprocess.run(command, capture_output=True, env=env)
    return len(run.stdout) + len(run.stderr), run.returncode

base = "9cdf66f805adc7a710a4f517a2829fae96c49525..daae1bfff06e5bf0f67068372c4f6cf02d68d9dd"
fixture = "specs/001-codex-native-hook/fixtures/failing-rust/Cargo.toml"
raw_env = {**os.environ, "CARGO_TARGET_DIR": "target/codex-corpus/raw"}
rtk_env = {**os.environ, "CARGO_TARGET_DIR": "target/codex-corpus/filtered"}
cases = [
    (["git", "log", "--all", "--stat", "--oneline"], ["./target/release/rtk", "git", "log", "--all", "--stat", "--oneline"], None, None),
    (["git", "diff", base], ["./target/release/rtk", "git", "diff", base], None, None),
    (["find", ".", "-type", "f"], ["./target/release/rtk", "find", ".", "-type", "f"], None, None),
    (["rg", "-n", "test", "src"], ["./target/release/rtk", "rg", "-n", "test", "src"], None, None),
    (["cargo", "test", "--manifest-path", fixture], ["./target/release/rtk", "cargo", "test", "--manifest-path", fixture], raw_env, rtk_env),
]
for raw, filtered, raw_env, filtered_env in cases:
    print(measure(raw, raw_env), measure(filtered, filtered_env))
```

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

For `daae1bfff06e5bf0f67068372c4f6cf02d68d9dd`, the recorded median was
**8.770 ms**, p95 **9.649 ms**, maximum **10.498 ms**.

## Historical fixed-candidate Focused Check

- Candidate: `9838e31df58e9b8fe4872235de897ae311e45d3f`.
- Scope: `src/main.rs`, `src/hooks/{hook_cmd,init,constants,permissions}.rs`,
  `src/discover/registry.rs`, and `hooks/codex/README.md`.
- Consumers: Codex `PreToolUse`, CLI parsing, init/show/uninstall, shared registry.
- Command: `cargo test codex && cargo test discover::registry::tests`.
- Result: PASS — 23 Codex and 393 registry tests.
- Elapsed: 0.76 seconds; slowest step: registry tests at 0.25 seconds.
- Focused target: 60 seconds; met.

## Documentation Impact Classification

Classification: `documentation`. The owning Codex README and feature acceptance
record now describe installation, trust, restart, passthrough, rollback,
measured savings, and latency. No map or ADR was added because this is a
reversible local fork feature whose durable behavior is already discoverable
from those repository-local surfaces and commits.
