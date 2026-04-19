from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
STORE_SCRIPT = SCRIPT_DIR / "workking_store.py"


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def resolve_openclaw() -> str:
    for candidate in ("openclaw", "openclaw.cmd", "openclaw.exe"):
        found = shutil.which(candidate)
        if found:
            return found
    raise RuntimeError("openclaw executable not found in PATH")


def run_json(cmd: list[str], timeout: int | None = None) -> dict[str, Any]:
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout).strip() or f"command failed: {' '.join(cmd)}")
    stdout = completed.stdout.strip()
    return json.loads(stdout) if stdout else {"ok": True}


def store_command(*args: str) -> dict[str, Any]:
    return run_json([sys.executable, str(STORE_SCRIPT), *args])


def status_state() -> dict[str, Any]:
    return store_command("status")


def count_registered_handles(index_path: Path) -> int:
    if not index_path.exists():
        return 0
    data = json.loads(index_path.read_text(encoding="utf-8"))
    records = data.get("records", {})
    return len([key for key in records.keys() if "instagram.com/" not in str(key)])


def build_cycle_message(provider_order: list[str], batch_size: int) -> str:
    preferred = provider_order[0]
    fallbacks = ", ".join(provider_order[1:]) if len(provider_order) > 1 else "none"
    return (
        "Use the workking skill rules for Nepal Instagram creator discovery. "
        "Before searching, read the local registry index from ~/.openclaw/data/workking/instagram-nepal/registry/index.json "
        "or the OPENCLAW_STATE_DIR equivalent and ignore every stored handle and profile URL. "
        f"Use a single search cycle of exactly {batch_size} candidates before verification. "
        f"Preferred crawler/provider this cycle: {preferred}. "
        f"Fallback order if it fails or becomes noisy: {fallbacks}. "
        "Search only Instagram. Keep Nepal only, personal creator only, followers >= 100000, and strict evidence gates. "
        "Verify geography, persona, and follower evidence one profile at a time. "
        "As soon as one qualified and non-duplicate creator is found, write the payload through workking_store.py upsert-qualified, "
        "then stop the current cycle immediately so the runner can launch the next cycle. "
        "For duplicates, only update followers and updated_at through record-review. "
        "For unclear evidence, use EVIDENCE_GAP and do not register. "
        "Do not produce a chat report; update only the local files."
    )


def run_cycle(message: str, timeout_seconds: int) -> dict[str, Any]:
    cmd = [resolve_openclaw(), "agent", "--message", message, "--thinking", "medium", "--json"]
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": 124,
            "stdout": "",
            "stderr": f"cycle exceeded timeout of {timeout_seconds} seconds",
            "timed_out": True,
        }


def start() -> dict[str, Any]:
    run_info = store_command("start-run")
    index_path = Path(run_info["index_path"])
    provider_order = list(run_info["provider_order"])
    batch_size = int(run_info.get("batch_size", 8))
    single_cycle_timeout_seconds = int(run_info.get("single_cycle_timeout_seconds", 900))
    idle_stop_seconds = int(run_info.get("idle_stop_seconds", 1800))

    cycles: list[dict[str, Any]] = []

    while True:
        current = status_state()["state"]
        if current.get("status") != "running":
            return {"ok": True, "state": current, "cycles": cycles}

        before_count = count_registered_handles(index_path)
        result = run_cycle(build_cycle_message(provider_order, batch_size), single_cycle_timeout_seconds)
        after_count = count_registered_handles(index_path)
        new_unique = max(after_count - before_count, 0)

        store_command("complete-cycle", "--new-unique", str(new_unique))

        cycle_summary = {
            "finished_at": utc_now().isoformat().replace("+00:00", "Z"),
            "provider": provider_order[0],
            "new_unique": new_unique,
            "timed_out": bool(result.get("timed_out")),
            "returncode": result.get("returncode"),
            "stderr": result.get("stderr", ""),
        }
        cycles.append(cycle_summary)

        if new_unique > 0:
            provider_order = provider_order[1:] + provider_order[:1]
            time.sleep(1)
            continue

        refreshed = status_state()["state"]
        last_unique = parse_utc(refreshed.get("last_unique_qualified_at")) or utc_now()
        idle_seconds = int((utc_now() - last_unique).total_seconds())
        if idle_seconds >= idle_stop_seconds:
            finished = store_command("finish-run", "--stop-reason", f"no new unique qualified creator for {idle_stop_seconds} seconds")
            return {"ok": True, "state": finished["state"], "cycles": cycles}

        provider_order = provider_order[1:] + provider_order[:1]
        time.sleep(1)


def stop() -> dict[str, Any]:
    return store_command("stop-run")


def status() -> dict[str, Any]:
    return status_state()


def export(fmt: str) -> dict[str, Any]:
    return store_command("export", "--format", fmt)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start")
    sub.add_parser("stop")
    sub.add_parser("status")
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--format", choices=["markdown", "csv", "json"], default="markdown")
    args = parser.parse_args()

    try:
        if args.command == "start":
            result = start()
        elif args.command == "stop":
            result = stop()
        elif args.command == "status":
            result = status()
        else:
            result = export(args.format)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
