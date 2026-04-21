from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


SCRIPT_DIR = Path(__file__).resolve().parent
STORE_SCRIPT = SCRIPT_DIR / "workking_store.py"


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def seconds_since(started_at: str | None) -> int:
    started = parse_utc(started_at)
    if started is None:
        return 0
    return int((utc_now() - started).total_seconds())


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


def list_available_skills(timeout_seconds: int) -> set[str]:
    cmd = [resolve_openclaw(), "skills", "list"]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds, check=False)
    if completed.returncode != 0:
        return set()
    names: set[str] = set()
    for line in completed.stdout.splitlines():
        if "📦" not in line:
            continue
        segment = line.split("📦", 1)[1]
        name = segment.split("|", 1)[0].strip()
        if name:
            names.add(name)
    return names


def quick_url_check(url: str, headers: dict[str, str] | None, timeout_seconds: int) -> tuple[bool, str]:
    req = urlrequest.Request(url, headers=headers or {}, method="GET")
    try:
        with urlrequest.urlopen(req, timeout=timeout_seconds) as response:
            return True, f"http_{response.status}"
    except urlerror.HTTPError as exc:
        if 200 <= exc.code < 500:
            return True, f"http_{exc.code}"
        return False, f"http_{exc.code}"
    except Exception as exc:
        return False, exc.__class__.__name__


def probe_provider(provider: str, available_skills: set[str], timeout_seconds: int) -> dict[str, Any]:
    provider_lower = provider.strip().lower()
    if provider_lower == "openclaw-core":
        try:
            resolve_openclaw()
            return {
                "provider": provider,
                "ready": True,
                "reason": "openclaw_core_ready",
                "kind": "builtin",
            }
        except Exception as exc:
            return {
                "provider": provider,
                "ready": False,
                "reason": exc.__class__.__name__,
                "kind": "builtin",
            }

    if provider_lower in {"agent-reach", "autoglm-browser-agent", "search", "tavily"}:
        ready = provider_lower in available_skills
        return {
            "provider": provider,
            "ready": ready,
            "reason": "skill_ready" if ready else "skill_missing",
            "kind": "skill",
        }

    if provider_lower == "apify":
        token = os.environ.get("APIFY_TOKEN", "").strip()
        if not token:
            return {"provider": provider, "ready": False, "reason": "missing_apify_token", "kind": "api"}
        ok, reason = quick_url_check(
            f"https://api.apify.com/v2/users/me?token={token}",
            headers={"Accept": "application/json"},
            timeout_seconds=timeout_seconds,
        )
        return {"provider": provider, "ready": ok, "reason": reason, "kind": "api"}

    if provider_lower == "brightdata":
        api_key = os.environ.get("BRIGHTDATA_API_KEY", "").strip()
        if not api_key:
            return {"provider": provider, "ready": False, "reason": "missing_brightdata_api_key", "kind": "api"}
        state = status_state()["state"]
        health_url = (
            os.environ.get("BRIGHTDATA_HEALTHCHECK_URL", "").strip()
            or state.get("brightdata_healthcheck_url")
            or "https://api.brightdata.com/"
        )
        ok, reason = quick_url_check(
            health_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout_seconds=timeout_seconds,
        )
        return {"provider": provider, "ready": ok, "reason": reason, "kind": "api"}

    return {"provider": provider, "ready": False, "reason": "unknown_provider", "kind": "unknown"}


def select_provider_chain(provider_order: list[str], probe_timeout_seconds: int) -> tuple[list[str], list[dict[str, Any]]]:
    available_skills = list_available_skills(probe_timeout_seconds)
    probe_results = [probe_provider(provider, available_skills, probe_timeout_seconds) for provider in provider_order]
    ready_chain = [item["provider"] for item in probe_results if item.get("ready")]
    return ready_chain, probe_results


def build_cycle_message(
    provider_order: list[str],
    batch_size: int,
    active_province: str,
    province_order: list[str],
    candidate_cooldown_seconds: int,
    index_path: str,
) -> str:
    preferred = provider_order[0]
    fallbacks = ", ".join(provider_order[1:]) if len(provider_order) > 1 else "none"
    province_scope = ", ".join(province_order) if province_order else "Nepal"
    return (
        "Use the workking skill rules for Nepal Instagram creator discovery. "
        f"Before searching, read the local registry index from {index_path} "
        "and ignore every stored handle and profile URL. "
        f"Use a single search cycle of exactly {batch_size} candidates before verification. "
        f"Current province focus: {active_province}. "
        f"Province rotation set: {province_scope}. "
        "Search only inside the current province focus for this entire run. "
        "Do not do Nepal-wide discovery and then discard out-of-region accounts. "
        "All search queries, location pages, keyword combinations, and candidate discovery steps must be scoped to the current province first. "
        f"Throttle the workflow so there is at least {candidate_cooldown_seconds} seconds between each individual candidate search or profile verification action. "
        "This cooldown applies between one creator lookup and the next creator lookup. "
        f"Preferred crawler/provider this cycle: {preferred}. "
        f"Fallback order if it fails or becomes noisy: {fallbacks}. "
        "Search only Instagram. Keep Nepal only, personal creator only, followers >= 100000, and strict evidence gates. "
        "If provider is openclaw-core, use only the built-in OpenClaw browsing, fetch, and search capabilities available in this environment. "
        "Verify geography, persona, and follower evidence one profile at a time. "
        "As soon as one qualified and non-duplicate creator is found, write the payload through workking_store.py upsert-qualified, "
        "then stop the current cycle immediately so the runner can launch the next cycle. "
        "For duplicates, only update followers and updated_at through record-review. "
        "For unclear evidence, use EVIDENCE_GAP and do not register. "
        "If a provider reports an Instagram session suspension, login failure, checkpoint, or account disablement, treat that as a provider failure only. "
        "Do not stop the whole task for that reason. Return control so the runner can switch to the next provider automatically. "
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


def spawn_background_worker() -> int:
    cmd = [sys.executable, str(Path(__file__).resolve()), "run-loop"]
    kwargs: dict[str, Any] = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, **kwargs)
    return int(proc.pid)


def start(province: str | None = None, trigger_command: str | None = None) -> dict[str, Any]:
    current = status_state()
    if current["state"].get("status") == "running":
        return {
            "ok": True,
            "result": "already_running",
            "state": current["state"],
            "active_province": current.get("active_province"),
            "worker_pid": current["state"].get("worker_pid"),
        }

    cmd = ["start-run"]
    if province:
        cmd.extend(["--province", province])
    if trigger_command:
        cmd.extend(["--trigger-command", trigger_command])
    run_info = store_command(*cmd)
    worker_pid = spawn_background_worker()
    store_command("attach-worker", "--pid", str(worker_pid))
    current = status_state()
    return {
        "ok": True,
        "result": "started",
        "worker_pid": worker_pid,
        "state": current["state"],
        "active_province": current.get("active_province"),
        "data_root": current.get("data_root"),
    }


def run_loop() -> dict[str, Any]:
    current_info = status_state()
    if current_info["state"].get("status") != "running":
        return {"ok": True, "result": "not_running"}

    index_path = Path(current_info["index_path"])
    run_info = current_info
    index_path = Path(run_info["index_path"])
    provider_order = list(run_info["state"].get("active_provider_order") or run_info["state"]["provider_order"])
    province_order = list(run_info["state"].get("province_order", []))
    batch_size = int(run_info["state"].get("batch_size", 5))
    candidate_cooldown_seconds = int(run_info["state"].get("candidate_cooldown_seconds", 300))
    provider_retry_cooldown_seconds = int(run_info["state"].get("provider_retry_cooldown_seconds", 30))
    single_cycle_timeout_seconds = int(run_info["state"].get("single_cycle_timeout_seconds", 10800))
    idle_stop_seconds = int(run_info["state"].get("idle_stop_seconds", 10800))
    max_run_seconds = int(run_info["state"].get("max_run_seconds", 10800))
    provider_probe_timeout_seconds = int(run_info["state"].get("provider_probe_timeout_seconds", 5))
    active_province = str(run_info["state"].get("last_active_province") or "Nepal")

    cycles: list[dict[str, Any]] = []

    while True:
        current_info = status_state()
        current = current_info["state"]
        if current.get("status") != "running":
            return {"ok": True, "state": current, "cycles": cycles}
        if seconds_since(current.get("run_started_at")) >= max_run_seconds:
            finished = store_command("finish-run", "--stop-reason", f"max run window reached ({max_run_seconds} seconds)")
            return {"ok": True, "state": finished["state"], "cycles": cycles}

        ready_chain, probe_results = select_provider_chain(provider_order, provider_probe_timeout_seconds)
        probe_payload_path = Path(run_info["tmp_dir"]) / "provider_probes.json"
        probe_payload_path.write_text(json.dumps(probe_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        store_command("update-provider-probes", "--payload", str(probe_payload_path))

        if not ready_chain:
            refreshed = status_state()["state"]
            last_unique = parse_utc(refreshed.get("last_unique_qualified_at")) or utc_now()
            idle_seconds = int((utc_now() - last_unique).total_seconds())
            cycles.append(
                {
                    "finished_at": utc_now().isoformat().replace("+00:00", "Z"),
                    "provider": None,
                    "new_unique": 0,
                    "timed_out": False,
                    "returncode": None,
                    "stderr": "no ready providers after probing",
                    "province": active_province,
                    "probe_results": probe_results,
                }
            )
            if idle_seconds >= idle_stop_seconds:
                finished = store_command("finish-run", "--stop-reason", "no healthy providers and idle window exceeded")
                return {"ok": True, "state": finished["state"], "cycles": cycles}
            provider_order = provider_order[1:] + provider_order[:1]
            time.sleep(provider_retry_cooldown_seconds)
            continue

        before_count = count_registered_handles(index_path)
        active_chain = ready_chain + [provider for provider in provider_order if provider not in ready_chain]
        remaining_run_seconds = max_run_seconds - seconds_since(current.get("run_started_at"))
        cycle_timeout_seconds = max(
            60,
            min(
                single_cycle_timeout_seconds,
                max(remaining_run_seconds, 60),
            ),
        )
        result = run_cycle(
            build_cycle_message(
                active_chain,
                batch_size,
                active_province,
                province_order,
                candidate_cooldown_seconds,
                str(index_path),
            ),
            cycle_timeout_seconds,
        )
        after_count = count_registered_handles(index_path)
        new_unique = max(after_count - before_count, 0)

        store_command("complete-cycle", "--new-unique", str(new_unique))

        cycle_summary = {
            "finished_at": utc_now().isoformat().replace("+00:00", "Z"),
            "provider": ready_chain[0],
            "province": active_province,
            "batch_size": batch_size,
            "candidate_cooldown_seconds": candidate_cooldown_seconds,
            "new_unique": new_unique,
            "timed_out": bool(result.get("timed_out")),
            "returncode": result.get("returncode"),
            "stderr": result.get("stderr", ""),
            "probe_results": probe_results,
        }
        cycles.append(cycle_summary)

        if new_unique > 0:
            provider_order = provider_order[1:] + provider_order[:1]
            time.sleep(candidate_cooldown_seconds)
            continue

        refreshed = status_state()["state"]
        last_unique = parse_utc(refreshed.get("last_unique_qualified_at")) or utc_now()
        idle_seconds = int((utc_now() - last_unique).total_seconds())
        if idle_seconds >= idle_stop_seconds:
            finished = store_command("finish-run", "--stop-reason", f"no new unique qualified creator for {idle_stop_seconds} seconds")
            return {"ok": True, "state": finished["state"], "cycles": cycles}

        provider_order = provider_order[1:] + provider_order[:1]
        time.sleep(candidate_cooldown_seconds)


def stop() -> dict[str, Any]:
    return store_command("stop-run")


def status() -> dict[str, Any]:
    return status_state()


def export(fmt: str) -> dict[str, Any]:
    return store_command("export", "--format", fmt)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    start_parser = sub.add_parser("start")
    start_parser.add_argument("--province")
    start_parser.add_argument("--trigger-command")
    sub.add_parser("run-loop")
    sub.add_parser("stop")
    sub.add_parser("status")
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--format", choices=["markdown", "csv", "json"], default="markdown")
    args = parser.parse_args()

    try:
        if args.command == "start":
            result = start(args.province, args.trigger_command)
        elif args.command == "run-loop":
            result = run_loop()
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
