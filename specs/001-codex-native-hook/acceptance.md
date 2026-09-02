# Acceptance Evidence

**Production candidate**: `9838e31df58e9b8fe4872235de897ae311e45d3f`

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

The Codex adapter calls the same `decide_hook_action → get_rewritten →
rewrite_command → RULES` path as Claude. The exhaustive Codex payload corpus
asserted set equality and rewrote all **87/87 unique RTK targets exactly once**,
while emitting no permission fields. `cargo test hook_cmd` passed all 116 hook
tests. No Codex-specific registry exists.

## Byte savings

Combined stdout/stderr, raw outputs all above 1 KiB:

| Case | Raw bytes | Filtered bytes | Reduction | Status |
|---|---:|---:|---:|---:|
| Git log | 134,475 | 3,501 | 97.4% | 0 |
| Git diff | 169,277 | 21,492 | 87.3% | 0 |
| File listing | 5,047 | 5,047 | 0.0% | 0 |
| Text search | 375,538 | 17,089 | 95.4% | 0 |
| Failing Rust test | 4,688 | 4,433 | 5.4% | 101 |

Median: **87.3%**, above the operator's 30% gate. Status, failing test name,
failure count, and representative paths remained present.

## Latency

The initial release candidate measured 16.247 ms median and failed SC-005.
After lazy candidate-only registry compilation, 200 release-process hook
invocations measured **7.275 ms median** and 8.047 ms p95. SC-005 passes.

## Fixed-candidate Focused Check

- Candidate: `9838e31df58e9b8fe4872235de897ae311e45d3f`.
- Scope: `src/main.rs`, `src/hooks/{hook_cmd,init,constants}.rs`,
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
