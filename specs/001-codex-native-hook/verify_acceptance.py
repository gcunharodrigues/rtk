#!/usr/bin/env python3
"""Run the fixed RTK acceptance corpus and verify its preserved semantics."""

from __future__ import annotations

import io
import json
import os
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


BASE = "9cdf66f805adc7a710a4f517a2829fae96c49525"
PRODUCTION = "c89508aba6676ecd0f034895dea70f385110adad"
RANGE = f"{BASE}..{PRODUCTION}"
ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "target" / "codex-corpus"
PRODUCTION_SOURCE = CORPUS / "production-source"
PRODUCTION_TARGET = CORPUS / "production-target"
BINARY = PRODUCTION_TARGET / "release" / "rtk"
FIXTURE = "specs/001-codex-native-hook/fixtures/failing-rust/Cargo.toml"
RAW_TARGET = CORPUS / "raw"
FILTERED_TARGET = CORPUS / "filtered"
TEE_DIR = CORPUS / "tee"
ISOLATED_HOME = CORPUS / "home"


class VerificationError(RuntimeError):
    pass


def environment(*, filtered: bool = False, cargo_target: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(ISOLATED_HOME),
            "XDG_CONFIG_HOME": str(CORPUS / "config"),
            "XDG_DATA_HOME": str(CORPUS / "data"),
            "XDG_CACHE_HOME": str(CORPUS / "cache"),
            "CARGO_NET_OFFLINE": "1",
            "CARGO_TERM_COLOR": "never",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "LC_ALL": "C",
            "NO_COLOR": "1",
            "RUST_BACKTRACE": "0",
            "TERM": "dumb",
        }
    )
    if filtered:
        env.update(
            {
                "RTK_TEE_DIR": str(TEE_DIR),
                "RTK_HOOK_AUDIT": "0",
                "RTK_DB_PATH": str(CORPUS / "tracking.db"),
            }
        )
    if cargo_target is not None:
        env["CARGO_TARGET_DIR"] = str(cargo_target)
    return env


def run(command: list[str], env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise VerificationError(f"could not run {' '.join(command)}: {exc}") from exc


def output(result: subprocess.CompletedProcess[bytes]) -> bytes:
    return result.stdout + result.stderr


def text(result: subprocess.CompletedProcess[bytes]) -> str:
    return output(result).decode("utf-8", errors="replace")


def recovery_paths(value: str, cwd: Path) -> tuple[list[Path], bool]:
    paths: list[Path] = []
    malformed = False
    for match in re.finditer(r"\[(?:full output|see remaining):\s*([^\]]+)\]", value):
        try:
            parts = shlex.split(match.group(1))
        except ValueError:
            malformed = True
            continue
        if not parts:
            malformed = True
            continue
        token = parts[-1]
        if token == "~" or token.startswith("~/"):
            token = str(ISOLATED_HOME) + token[1:]
        token = token.replace("$HOME", str(ISOLATED_HOME))
        path = Path(token)
        if not path.is_absolute():
            path = cwd / path
        paths.append(path.resolve())
    return paths, malformed


def inside(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def recovery_contents(value: str, cwd: Path) -> tuple[list[Path], list[str], bool]:
    paths, malformed = recovery_paths(value, cwd)
    contents: list[str] = []
    for path in paths:
        if inside(path, TEE_DIR) and path.is_file():
            contents.append(path.read_text(encoding="utf-8", errors="replace"))
    exists = bool(paths) and not malformed and all(inside(path, TEE_DIR) and path.is_file() for path in paths)
    return paths, contents, exists


def base_semantics(raw: subprocess.CompletedProcess[bytes], filtered: subprocess.CompletedProcess[bytes]) -> dict[str, bool]:
    return {
        "status_preserved": raw.returncode == filtered.returncode,
        "raw_above_1KiB": len(output(raw)) > 1024,
    }


def record(
    name: str,
    raw: subprocess.CompletedProcess[bytes],
    filtered: subprocess.CompletedProcess[bytes],
    semantics: dict[str, bool],
) -> tuple[dict[str, object], float]:
    semantics["ok"] = all(semantics.values())
    raw_bytes = len(output(raw))
    filtered_bytes = len(output(filtered))
    reduction = 100.0 * (raw_bytes - filtered_bytes) / raw_bytes if raw_bytes else -100.0
    return (
        {
            "raw_bytes": raw_bytes,
            "filtered_bytes": filtered_bytes,
            "reduction": round(reduction, 1),
            "raw_status": raw.returncode,
            "filtered_status": filtered.returncode,
            "semantic": semantics,
        },
        reduction,
    )


def log_commit_count(value: str) -> int:
    return len(re.findall(r"(?m)^[0-9a-f]{7,40}(?:\s|$)", value))


def diff_paths(value: str) -> list[str]:
    paths: list[str] = []
    for line in value.splitlines():
        if not line.startswith("diff --git "):
            continue
        rest = line[len("diff --git ") :]
        if " b/" in rest:
            paths.append(rest.split(" b/", 1)[1])
    return paths


def find_path_visible(path: str, value: str) -> bool:
    if path in value:
        return True
    parent, _, name = path.rpartition("/")
    if not parent:
        return False
    return bool(re.search(rf"(?m)^{re.escape(parent)}/\s+[^\n]*\b{re.escape(name)}(?:\s|$)", value))


def shortstat_counts(value: str) -> tuple[int, int, int] | None:
    pattern = re.compile(
        r"^\s*(\d+) files? changed"
        r"(?:,\s*(\d+) insertions?\(\+\))?"
        r"(?:,\s*(\d+) deletions?\(-\))?\s*$"
    )
    for line in value.splitlines():
        match = pattern.match(line)
        if match:
            return (
                int(match.group(1)),
                int(match.group(2) or 0),
                int(match.group(3) or 0),
            )
    return None


def diff_summary_semantics(raw_value: str, filtered_value: str) -> dict[str, bool]:
    raw_counts = shortstat_counts(raw_value)
    filtered_counts = shortstat_counts(filtered_value)
    return {
        "changed_file_count_preserved": raw_counts is not None
        and filtered_counts is not None
        and raw_counts[0] == filtered_counts[0],
        "insertions_preserved": raw_counts is not None
        and filtered_counts is not None
        and raw_counts[1] == filtered_counts[1],
        "deletions_preserved": raw_counts is not None
        and filtered_counts is not None
        and raw_counts[2] == filtered_counts[2],
    }


def rg_match_keys(value: str) -> list[tuple[str, int]]:
    matches: list[tuple[str, int]] = []
    for line in value.splitlines():
        match = re.match(r"^(.+?):(\d+):", line)
        if match:
            matches.append((match.group(1), int(match.group(2))))
    return matches


def rg_coverage(raw_value: str, filtered_value: str, recovered_contents: list[str]) -> dict[str, bool]:
    raw_keys = set(rg_match_keys(raw_value))
    visible_keys = set(rg_match_keys(filtered_value))
    recovered_sets = [set(rg_match_keys(content)) for content in recovered_contents]
    recovered_keys = set().union(*recovered_sets) if recovered_sets else set()
    return {
        "all_raw_keys_recoverable": bool(raw_keys) and raw_keys <= visible_keys | recovered_keys,
        "hidden_raw_key_recovered": bool((raw_keys - visible_keys) & recovered_keys),
        "recovery_contents_relevant": bool(recovered_sets)
        and all(keys and keys <= raw_keys for keys in recovered_sets),
    }


def verify_log(raw: subprocess.CompletedProcess[bytes], filtered: subprocess.CompletedProcess[bytes]) -> dict[str, bool]:
    raw_value = text(raw)
    filtered_value = text(filtered)
    semantics = base_semantics(raw, filtered)
    semantics.update(
        {
            "output_equal": output(raw) == output(filtered),
            "commit_count_preserved": log_commit_count(raw_value) == log_commit_count(filtered_value)
            and log_commit_count(raw_value) > 0,
        }
    )
    return semantics


def verify_diff(
    raw: subprocess.CompletedProcess[bytes],
    filtered: subprocess.CompletedProcess[bytes],
    raw_shortstat: subprocess.CompletedProcess[bytes],
) -> dict[str, bool]:
    raw_paths = diff_paths(text(raw))
    filtered_value = text(filtered)
    raw_counts = shortstat_counts(text(raw_shortstat))
    semantics = base_semantics(raw, filtered)
    summary = diff_summary_semantics(text(raw_shortstat), filtered_value)
    summary["changed_file_count_preserved"] = (
        summary["changed_file_count_preserved"]
        and raw_counts is not None
        and len(set(raw_paths)) == len(raw_paths) == raw_counts[0]
    )
    semantics.update(
        {
            "changed_paths_preserved": bool(raw_paths) and all(path in filtered_value for path in raw_paths),
            "raw_shortstat_succeeded": raw_shortstat.returncode == 0,
            **summary,
        }
    )
    return semantics


def verify_find(raw: subprocess.CompletedProcess[bytes], filtered: subprocess.CompletedProcess[bytes]) -> dict[str, bool]:
    raw_paths = [line for line in text(raw).splitlines() if line]
    filtered_value = text(filtered)
    header = re.search(r"(?m)^(\d+)F\s+\d+D:", filtered_value)
    paths, contents, recovery_ok = recovery_contents(filtered_value, PRODUCTION_SOURCE)
    representatives = [
        path
        for path in (
            "src/main.rs",
            "docs/TELEMETRY.md",
            "hooks/codex/README.md",
            "specs/001-codex-native-hook/spec.md",
        )
        if path in raw_paths
    ]
    visible_or_recovered = lambda path: find_path_visible(path, filtered_value) or any(path in content for content in contents)
    hidden_recovered = any(
        path not in filtered_value and any(path in content for content in contents)
        for path in raw_paths
    )
    semantics = base_semantics(raw, filtered)
    semantics.update(
        {
            "file_count_preserved": bool(header) and int(header.group(1)) == len(raw_paths),
            "representative_paths_present": bool(representatives) and all(visible_or_recovered(path) for path in representatives),
            "truncation_marker": bool(re.search(r"(?m)^\+\d+ more(?:\s|$)", filtered_value)),
            "recovery_hint": bool(paths),
            "recovery_paths_exist": recovery_ok,
            "hidden_raw_path_recovered": hidden_recovered,
        }
    )
    return semantics


def verify_rg(raw: subprocess.CompletedProcess[bytes], filtered: subprocess.CompletedProcess[bytes]) -> dict[str, bool]:
    raw_value = text(raw)
    raw_matches = rg_match_keys(raw_value)
    raw_paths = [path for path, _ in raw_matches]
    filtered_value = text(filtered)
    header = re.search(r"(?m)^(\d+) matches in (\d+) files:", filtered_value)
    paths, contents, recovery_ok = recovery_contents(filtered_value, PRODUCTION_SOURCE)
    representative = "src/main.rs" if "src/main.rs" in raw_paths else (sorted(set(raw_paths))[0] if raw_paths else "")
    semantics = base_semantics(raw, filtered)
    semantics.update(
        {
            "match_count_preserved": bool(header) and int(header.group(1)) == len(raw_matches),
            "unique_file_count_preserved": bool(header) and int(header.group(2)) == len(set(raw_paths)),
            "representative_path_recovered": bool(representative)
            and (representative in filtered_value or any(representative in content for content in contents)),
            "truncation_marker": bool(re.search(r"\+\d+ more(?:\s|$)", filtered_value)),
            "recovery_hint": bool(paths),
            "recovery_paths_exist": recovery_ok,
            **rg_coverage(raw_value, filtered_value, contents),
        }
    )
    return semantics


def verify_failure(raw: subprocess.CompletedProcess[bytes], filtered: subprocess.CompletedProcess[bytes]) -> dict[str, bool]:
    filtered_value = text(filtered)
    semantics = base_semantics(raw, filtered)
    semantics.update(
        {
            "status_101": raw.returncode == 101 and filtered.returncode == 101,
            "failure_identity_preserved": "preserves_failure_details" in filtered_value,
            "failure_summary_preserved": "1 failed" in filtered_value,
        }
    )
    return semantics


def validate_corpus_paths(root: Path, corpus: Path) -> Path:
    target = root / "target"
    if target.is_symlink():
        raise VerificationError(f"refusing symlinked target directory: {target}")
    if corpus.is_symlink():
        raise VerificationError(f"refusing symlinked corpus directory: {corpus}")
    target_real = target.resolve()
    corpus_real = corpus.resolve()
    if corpus.parent != target or corpus_real.parent != target_real:
        raise VerificationError(f"corpus is not a direct child of target: {corpus}")
    return corpus_real


def initialize_corpus(root: Path, corpus: Path) -> Path:
    expected = validate_corpus_paths(root, corpus)
    target = root / "target"
    try:
        target.mkdir(exist_ok=True)
        validate_corpus_paths(root, corpus)
        corpus.mkdir(exist_ok=True)
    except OSError as exc:
        raise VerificationError(f"could not initialize corpus {corpus}: {exc}") from exc
    actual = validate_corpus_paths(root, corpus)
    if actual != expected:
        raise VerificationError(f"corpus path changed during initialization: {corpus}")
    return actual


def validate_managed_path(path: Path, root: Path, corpus: Path, corpus_real: Path) -> None:
    if validate_corpus_paths(root, corpus) != corpus_real:
        raise VerificationError(f"validated corpus changed: {corpus}")
    if path.parent != corpus or path.parent.resolve() != corpus_real:
        raise VerificationError(f"refusing managed path outside corpus: {path}")


def recreate_directory(path: Path, root: Path, corpus: Path, corpus_real: Path) -> None:
    validate_managed_path(path, root, corpus, corpus_real)
    if path.is_symlink():
        path.unlink()
    elif path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    validate_managed_path(path, root, corpus, corpus_real)
    path.mkdir()


def symlink_corpus_self_test() -> bool:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        root = base / "root"
        target = root / "target"
        outside = base / "outside"
        root.mkdir()
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_bytes(b"untouched")
        corpus = target / "codex-corpus"
        corpus.symlink_to(outside, target_is_directory=True)
        try:
            initialize_corpus(root, corpus)
        except VerificationError:
            rejected = True
        else:
            rejected = False
        untouched = corpus.is_symlink() and sentinel.read_bytes() == b"untouched"
        result = rejected and untouched
        assert result, "symlinked corpus touched its outside target"
        return result


def adversarial_self_tests() -> dict[str, bool]:
    raw_shortstat = " 22 files changed, 1438 insertions(+), 98 deletions(-)\n"
    false_shortstats = {
        "false_diff_files_rejected": " 999 files changed, 1438 insertions(+), 98 deletions(-)\n",
        "false_diff_insertions_rejected": " 22 files changed, 999 insertions(+), 98 deletions(-)\n",
        "false_diff_deletions_rejected": " 22 files changed, 1438 insertions(+), 999 deletions(-)\n",
    }
    diff_checks = {
        name: not all(diff_summary_semantics(raw_shortstat, false_value).values())
        for name, false_value in false_shortstats.items()
    }
    assert all(diff_checks.values()), "false diff counts were accepted"

    raw_rg = "src/a.rs:1:test\nsrc/b.rs:2:test\n"
    visible_rg = "2 matches in 2 files:\n\nsrc/a.rs:1:test\n+1 more\n"
    irrelevant = rg_coverage(
        raw_rg,
        visible_rg,
        ["src/b.rs:2:test\n", "src/irrelevant.rs:9:test\n"],
    )
    irrelevant_rg_recovery_rejected = not all(irrelevant.values())
    assert irrelevant_rg_recovery_rejected, "irrelevant rg recovery was accepted"
    assert all(rg_coverage(raw_rg, visible_rg, ["src/b.rs:2:test\n"]).values())
    return {
        **diff_checks,
        "irrelevant_rg_recovery_rejected": irrelevant_rg_recovery_rejected,
        "symlinked_corpus_rejected_without_touching_sentinel": symlink_corpus_self_test(),
    }


def prepare_production(expected_corpus: Path) -> None:
    corpus_real = initialize_corpus(ROOT, CORPUS)
    if corpus_real != expected_corpus:
        raise VerificationError(f"corpus path changed before initialization: {CORPUS}")
    recreate_directory(ISOLATED_HOME, ROOT, CORPUS, corpus_real)
    ancestor = run(
        ["git", "merge-base", "--is-ancestor", PRODUCTION, "HEAD"],
        environment(),
        ROOT,
    )
    if ancestor.returncode != 0:
        raise VerificationError(f"production {PRODUCTION} is not an ancestor of HEAD")

    archived = run(["git", "archive", "--format=tar", PRODUCTION], environment(), ROOT)
    if archived.returncode != 0:
        raise VerificationError(f"git archive failed (status {archived.returncode}): {text(archived).strip()}")

    recreate_directory(PRODUCTION_SOURCE, ROOT, CORPUS, corpus_real)
    recreate_directory(PRODUCTION_TARGET, ROOT, CORPUS, corpus_real)
    recreate_directory(TEE_DIR, ROOT, CORPUS, corpus_real)
    validate_managed_path(PRODUCTION_SOURCE, ROOT, CORPUS, corpus_real)
    try:
        with tarfile.open(fileobj=io.BytesIO(archived.stdout), mode="r:") as archive:
            archive.extractall(PRODUCTION_SOURCE, filter="data")
    except (OSError, tarfile.TarError) as exc:
        raise VerificationError(f"could not extract production archive: {exc}") from exc

    build_env = os.environ.copy()
    build_env.update(
        {
            "CARGO_TARGET_DIR": str(PRODUCTION_TARGET),
            "CARGO_TERM_COLOR": "never",
            "NO_COLOR": "1",
        }
    )
    validate_managed_path(PRODUCTION_TARGET, ROOT, CORPUS, corpus_real)
    built = run(["cargo", "build", "--release", "--offline"], build_env, PRODUCTION_SOURCE)
    if built.returncode != 0:
        raise VerificationError(f"production build failed (status {built.returncode}): {text(built).strip()}")
    if not BINARY.is_file() or not os.access(BINARY, os.X_OK):
        raise VerificationError(f"production build did not create executable: {BINARY}")


def clean_fixture_targets(corpus_real: Path) -> None:
    for target in (RAW_TARGET, FILTERED_TARGET):
        recreate_directory(target, ROOT, CORPUS, corpus_real)
        result = run(
            ["cargo", "clean", "--manifest-path", FIXTURE],
            environment(cargo_target=target),
            PRODUCTION_SOURCE,
        )
        if result.returncode != 0:
            detail = text(result).strip().replace("\n", " ")
            raise VerificationError(f"cargo clean failed for {target} (status {result.returncode}): {detail}")


def main() -> int:
    expected_corpus = validate_corpus_paths(ROOT, CORPUS)
    adversarial = adversarial_self_tests()
    prepare_production(expected_corpus)
    clean_fixture_targets(expected_corpus)
    cases: dict[str, dict[str, object]] = {}
    reductions: list[float] = []

    commands = [
        (
            "git_log",
            ["git", "log", "--stat", "--oneline", RANGE],
            [str(BINARY), "git", "log", "--stat", "--oneline", RANGE],
            verify_log,
            None,
            ROOT,
        ),
        (
            "git_diff",
            ["git", "diff", RANGE],
            [str(BINARY), "git", "diff", RANGE],
            verify_diff,
            None,
            ROOT,
        ),
        (
            "find",
            ["find", "src", "docs", "hooks", "specs", "-type", "f"],
            [str(BINARY), "find", "src", "docs", "hooks", "specs", "-type", "f"],
            verify_find,
            None,
            PRODUCTION_SOURCE,
        ),
        (
            "rg",
            ["rg", "-n", "test", "src"],
            [str(BINARY), "rg", "-n", "test", "src"],
            verify_rg,
            None,
            PRODUCTION_SOURCE,
        ),
        (
            "failing_rust_test",
            ["cargo", "test", "--verbose", "--manifest-path", FIXTURE],
            [str(BINARY), "cargo", "test", "--verbose", "--manifest-path", FIXTURE],
            verify_failure,
            (RAW_TARGET, FILTERED_TARGET),
            PRODUCTION_SOURCE,
        ),
    ]

    for name, raw_command, filtered_command, verifier, cargo_targets, cwd in commands:
        raw_env = environment(cargo_target=cargo_targets[0]) if cargo_targets else environment()
        filtered_env = environment(filtered=True, cargo_target=cargo_targets[1]) if cargo_targets else environment(filtered=True)
        if validate_corpus_paths(ROOT, CORPUS) != expected_corpus:
            raise VerificationError(f"validated corpus changed before raw command: {CORPUS}")
        if cargo_targets:
            validate_managed_path(cargo_targets[0], ROOT, CORPUS, expected_corpus)
        raw = run(raw_command, raw_env, cwd)
        if validate_corpus_paths(ROOT, CORPUS) != expected_corpus:
            raise VerificationError(f"validated corpus changed before filtered command: {CORPUS}")
        validate_managed_path(TEE_DIR, ROOT, CORPUS, expected_corpus)
        if cargo_targets:
            validate_managed_path(cargo_targets[1], ROOT, CORPUS, expected_corpus)
        filtered = run(filtered_command, filtered_env, cwd)
        if name == "git_diff":
            raw_shortstat = run(["git", "diff", "--shortstat", RANGE], environment(), ROOT)
            semantics = verifier(raw, filtered, raw_shortstat)
        else:
            semantics = verifier(raw, filtered)
        case, reduction = record(name, raw, filtered, semantics)
        cases[name] = case
        reductions.append(reduction)

    median = statistics.median(reductions)
    ok = all(adversarial.values()) and all(case["semantic"]["ok"] for case in cases.values()) and median >= 30.0
    result = {
        "base": BASE,
        "production": PRODUCTION,
        "adversarial_checks": adversarial,
        "cases": cases,
        "median_reduction": round(median, 1),
        "median_at_least_30_percent": median >= 30.0,
        "ok": ok,
    }
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"verify_acceptance.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
