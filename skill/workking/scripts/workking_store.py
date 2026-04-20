from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def default_data_root() -> Path:
    state_dir = os.environ.get("OPENCLAW_STATE_DIR")
    if state_dir:
        return Path(state_dir).expanduser().resolve() / "data" / "workking" / "instagram-nepal"
    return Path.home() / ".openclaw" / "data" / "workking" / "instagram-nepal"


def default_config_root() -> Path:
    state_dir = os.environ.get("OPENCLAW_STATE_DIR")
    if state_dir:
        return Path(state_dir).expanduser().resolve() / "data" / "workking"
    return Path.home() / ".openclaw" / "data" / "workking"


DATA_ROOT = default_data_root()
CONFIG_ROOT = default_config_root()
CONFIG_PATH = CONFIG_ROOT / "workking.config.json"
REGISTRY_DIR = DATA_ROOT / "registry"
CREATORS_DIR = REGISTRY_DIR / "creators"
EVIDENCE_DIR = DATA_ROOT / "evidence" / "reviews"
EXPORTS_DIR = DATA_ROOT / "exports"
TMP_DIR = DATA_ROOT / "tmp"
RUNTIME_DIR = DATA_ROOT / "runtime"
INDEX_PATH = REGISTRY_DIR / "index.json"
STATE_PATH = RUNTIME_DIR / "state.json"
PENDING_PATH = EXPORTS_DIR / "pending_submissions.json"


def ensure_dirs() -> None:
    for path in (CONFIG_ROOT, CREATORS_DIR, EVIDENCE_DIR, EXPORTS_DIR, TMP_DIR, RUNTIME_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    ensure_dirs()
    return read_json(
        CONFIG_PATH,
        {
            "provider_order": [
                "agent-reach",
                "autoglm-browser-agent",
                "search",
                "openclaw-core",
                "apify",
                "brightdata",
            ],
            "batch_size": 5,
            "candidate_cooldown_seconds": 300,
            "provider_retry_cooldown_seconds": 30,
            "single_cycle_timeout_seconds": 10800,
            "idle_stop_seconds": 10800,
            "max_run_seconds": 10800,
            "provider_probe_timeout_seconds": 5,
            "province_switch_seconds": 1800,
            "province_order": [
                "Koshi Province",
                "Madhesh Province",
                "Bagmati Province",
                "Gandaki Province",
                "Lumbini Province",
                "Karnali Province",
                "Sudurpashchim Province",
            ],
            "brightdata_healthcheck_url": "https://api.brightdata.com/",
        },
    )


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "creator"


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    url = re.sub(r"\?.*$", "", url)
    url = url.rstrip("/")
    if url and not url.startswith("http"):
        url = f"https://{url.lstrip('/')}"
    return url.lower()


def extract_handle(url: str, fallback: str = "") -> str:
    match = re.search(r"instagram\.com/([^/?#]+)", normalize_url(url))
    if match:
        return match.group(1).lower()
    return fallback.strip().lstrip("@").lower()


def parse_followers(raw: Any) -> int:
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    text = str(raw or "").strip().lower().replace(",", "")
    if not text:
        raise ValueError("followers value missing")
    multiplier = 1
    if text.endswith("k"):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1000000
        text = text[:-1]
    return int(float(text) * multiplier)


def load_index() -> dict[str, Any]:
    return read_json(
        INDEX_PATH,
        {
            "platform": "instagram",
            "region": "Nepal",
            "submitted_handles": [],
            "records": {},
            "updated_at": utc_now(),
        },
    )


def save_index(index: dict[str, Any]) -> None:
    index["updated_at"] = utc_now()
    write_json(INDEX_PATH, index)


def load_state() -> dict[str, Any]:
    config = load_config()
    return read_json(
        STATE_PATH,
        {
            "trigger_command": "/workking",
            "status": "idle",
            "provider_cursor": 0,
            "provider_order": list(config.get("provider_order", [])),
            "batch_size": int(config.get("batch_size", 5)),
            "candidate_cooldown_seconds": int(config.get("candidate_cooldown_seconds", 300)),
            "provider_retry_cooldown_seconds": int(config.get("provider_retry_cooldown_seconds", 30)),
            "single_cycle_timeout_seconds": int(config.get("single_cycle_timeout_seconds", 10800)),
            "idle_stop_seconds": int(config.get("idle_stop_seconds", 10800)),
            "max_run_seconds": int(config.get("max_run_seconds", 10800)),
            "provider_probe_timeout_seconds": int(config.get("provider_probe_timeout_seconds", 5)),
            "province_order": list(config.get("province_order", [])),
            "province_cursor": 0,
            "province_switch_seconds": int(config.get("province_switch_seconds", 1800)),
            "run_province_base_cursor": 0,
            "last_active_province": None,
            "run_started_at": None,
            "run_finished_at": None,
            "last_unique_qualified_at": None,
            "last_stop_reason": None,
            "total_cycles": 0,
            "total_new_unique": 0,
            "last_provider_probe_results": [],
            "updated_at": utc_now(),
        },
    )


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    write_json(STATE_PATH, state)


def compute_runtime_province(state: dict[str, Any]) -> str | None:
    provinces = list(state.get("province_order", []))
    if not provinces:
        return None
    run_started_at = parse_utc(state.get("run_started_at"))
    if run_started_at is None:
        cursor = int(state.get("province_cursor", 0)) % len(provinces)
        return provinces[cursor]
    switch_seconds = max(int(state.get("province_switch_seconds", 1800)), 1)
    base_cursor = int(state.get("run_province_base_cursor", state.get("province_cursor", 0))) % len(provinces)
    elapsed_windows = int((datetime.now(timezone.utc) - run_started_at).total_seconds() // switch_seconds)
    return provinces[(base_cursor + elapsed_windows) % len(provinces)]


def compute_remaining_run_seconds(state: dict[str, Any]) -> int | None:
    run_started_at = parse_utc(state.get("run_started_at"))
    if run_started_at is None:
        return None
    max_run_seconds = max(int(state.get("max_run_seconds", 10800)), 1)
    remaining = max_run_seconds - int((datetime.now(timezone.utc) - run_started_at).total_seconds())
    return max(remaining, 0)


def compute_remaining_province_window_seconds(state: dict[str, Any]) -> int | None:
    run_started_at = parse_utc(state.get("run_started_at"))
    if run_started_at is None:
        return None
    switch_seconds = max(int(state.get("province_switch_seconds", 1800)), 1)
    elapsed = int((datetime.now(timezone.utc) - run_started_at).total_seconds())
    consumed = elapsed % switch_seconds
    remaining = switch_seconds - consumed
    return remaining if remaining > 0 else switch_seconds


def load_pending() -> dict[str, Any]:
    return read_json(
        PENDING_PATH,
        {
            "platform": "instagram",
            "region": "Nepal",
            "items": [],
            "updated_at": utc_now(),
        },
    )


def save_pending(payload: dict[str, Any]) -> None:
    payload["updated_at"] = utc_now()
    write_json(PENDING_PATH, payload)


@dataclass
class ReviewPayload:
    creator_name: str
    profile_url: str
    followers: str
    decision: str
    geography_status: str
    persona_status: str
    followers_status: str
    geography_evidence: str
    persona_evidence: str
    followers_evidence: str
    evidence_summary: str
    evidence_refs: list[str]

    @property
    def normalized_url(self) -> str:
        return normalize_url(self.profile_url)

    @property
    def handle(self) -> str:
        return extract_handle(self.profile_url, self.creator_name)

    @property
    def followers_count(self) -> int:
        return parse_followers(self.followers)


def load_payload(path: Path) -> ReviewPayload:
    raw = read_json(path, None)
    if not isinstance(raw, dict):
        raise ValueError("payload must be a JSON object")
    return ReviewPayload(
        creator_name=str(raw.get("creator_name", "")).strip(),
        profile_url=str(raw.get("profile_url", "")).strip(),
        followers=str(raw.get("followers", "")).strip(),
        decision=str(raw.get("decision", "")).strip().upper(),
        geography_status=str(raw.get("geography_status", "")).strip().upper(),
        persona_status=str(raw.get("persona_status", "")).strip().upper(),
        followers_status=str(raw.get("followers_status", "")).strip().upper(),
        geography_evidence=str(raw.get("geography_evidence", "")).strip(),
        persona_evidence=str(raw.get("persona_evidence", "")).strip(),
        followers_evidence=str(raw.get("followers_evidence", "")).strip(),
        evidence_summary=str(raw.get("evidence_summary", "")).strip(),
        evidence_refs=[str(item) for item in raw.get("evidence_refs", [])],
    )


def validate_payload(payload: ReviewPayload) -> None:
    if not payload.creator_name:
        raise ValueError("creator_name is required")
    if not payload.normalized_url or "instagram.com/" not in payload.normalized_url:
        raise ValueError("profile_url must be an Instagram profile URL")
    if not payload.handle:
        raise ValueError("unable to determine Instagram handle")
    if payload.decision not in {"QUALIFIED", "DUPLICATE", "SCREENED_FAIL", "EVIDENCE_GAP"}:
        raise ValueError("invalid decision")
    if payload.decision in {"QUALIFIED", "DUPLICATE"} and payload.followers_count < 100000:
        raise ValueError("qualified or duplicate entries must have followers >= 100000")


def evidence_filename(handle: str) -> str:
    return f"instagram-nepal-{slugify(handle)}-{slugify(utc_now())}.json"


def creator_filename(handle: str) -> str:
    return f"instagram-nepal-{slugify(handle)}.json"


def write_evidence(payload: ReviewPayload) -> str:
    rel = evidence_filename(payload.handle)
    out = EVIDENCE_DIR / rel
    write_json(
        out,
        {
            "platform": "instagram",
            "region": "Nepal",
            "creator_name": payload.creator_name,
            "profile_url": payload.normalized_url,
            "handle": payload.handle,
            "followers": payload.followers,
            "decision": payload.decision,
            "geography_status": payload.geography_status,
            "persona_status": payload.persona_status,
            "followers_status": payload.followers_status,
            "geography_evidence": payload.geography_evidence,
            "persona_evidence": payload.persona_evidence,
            "followers_evidence": payload.followers_evidence,
            "evidence_summary": payload.evidence_summary,
            "evidence_refs": payload.evidence_refs,
            "updated_at": utc_now(),
        },
    )
    return str(out)


def append_pending(entry: dict[str, Any], index: dict[str, Any]) -> None:
    handle = entry["handle"]
    if handle in set(index.get("submitted_handles", [])):
        return
    pending = load_pending()
    items = pending.get("items", [])
    if any(item.get("handle") == handle for item in items):
        return
    items.append(entry)
    pending["items"] = items
    save_pending(pending)


def build_creator_record(payload: ReviewPayload, evidence_path: str) -> dict[str, Any]:
    return {
        "creator_name": payload.creator_name,
        "profile_url": payload.normalized_url,
        "handle": payload.handle,
        "followers": payload.followers,
        "followers_count": payload.followers_count,
        "platform": "instagram",
        "region": "Nepal",
        "status": "registered",
        "updated_at": utc_now(),
        "evidence_path": evidence_path,
        "qualification": {
            "geography_status": payload.geography_status,
            "persona_status": payload.persona_status,
            "followers_status": payload.followers_status,
            "geography_evidence": payload.geography_evidence,
            "persona_evidence": payload.persona_evidence,
            "followers_evidence": payload.followers_evidence,
        },
        "evidence_summary": payload.evidence_summary,
    }


def upsert_qualified(payload: ReviewPayload) -> dict[str, Any]:
    if payload.decision != "QUALIFIED":
        raise ValueError("upsert-qualified requires decision=QUALIFIED")
    if payload.geography_status != "PASS" or payload.persona_status != "PASS" or payload.followers_status != "PASS":
        raise ValueError("qualified creators require PASS for geography, persona, and followers")

    evidence_path = write_evidence(payload)
    record = build_creator_record(payload, evidence_path)
    creator_path = CREATORS_DIR / creator_filename(payload.handle)
    existed = creator_path.exists()
    write_json(creator_path, record)

    index = load_index()
    entry = {
        "creator_file": str(creator_path),
        "handle": payload.handle,
        "profile_url": payload.normalized_url,
        "followers": payload.followers,
        "updated_at": utc_now(),
        "last_decision": "QUALIFIED",
    }
    index["records"][payload.handle] = entry
    index["records"][payload.normalized_url] = entry
    save_index(index)

    state = load_state()
    state["last_unique_qualified_at"] = utc_now()
    save_state(state)

    append_pending(
        {
            "creator_name": payload.creator_name,
            "profile_url": payload.normalized_url,
            "followers": payload.followers,
            "handle": payload.handle,
            "queued_at": utc_now(),
        },
        index,
    )
    return {"ok": True, "result": "updated_existing" if existed else "registered", "creator_file": str(creator_path)}


def record_review(payload: ReviewPayload) -> dict[str, Any]:
    evidence_path = write_evidence(payload)
    index = load_index()
    existing = index["records"].get(payload.handle) or index["records"].get(payload.normalized_url)
    if payload.decision == "DUPLICATE" and existing:
        creator_path = Path(existing["creator_file"])
        creator = read_json(creator_path, {})
        creator["followers"] = payload.followers
        creator["followers_count"] = payload.followers_count
        creator["updated_at"] = utc_now()
        creator["evidence_path"] = evidence_path
        write_json(creator_path, creator)
        existing["followers"] = payload.followers
        existing["updated_at"] = utc_now()
        existing["last_decision"] = "DUPLICATE"
        index["records"][payload.handle] = existing
        index["records"][payload.normalized_url] = existing
        save_index(index)
    return {"ok": True, "result": payload.decision.lower(), "evidence_path": evidence_path}


def start_run() -> dict[str, Any]:
    ensure_dirs()
    state = load_state()
    providers = list(state.get("provider_order", [])) or list(load_config().get("provider_order", []))
    if not providers:
        raise ValueError("provider_order cannot be empty")
    cursor = int(state.get("provider_cursor", 0)) % len(providers)
    rotated = providers[cursor:] + providers[:cursor]
    provinces = list(state.get("province_order", [])) or list(load_config().get("province_order", []))
    if not provinces:
        raise ValueError("province_order cannot be empty")
    province_cursor = int(state.get("province_cursor", 0)) % len(provinces)
    state["provider_cursor"] = (cursor + 1) % len(providers)
    state["status"] = "running"
    state["run_started_at"] = utc_now()
    state["run_finished_at"] = None
    state["last_unique_qualified_at"] = state["run_started_at"]
    state["run_province_base_cursor"] = province_cursor
    state["last_active_province"] = provinces[province_cursor]
    state["last_stop_reason"] = None
    state["total_cycles"] = 0
    state["total_new_unique"] = 0
    save_state(state)
    return {
        "ok": True,
        "data_root": str(DATA_ROOT),
        "index_path": str(INDEX_PATH),
        "pending_path": str(PENDING_PATH),
        "tmp_dir": str(TMP_DIR),
        "provider_order": rotated,
        "province_order": provinces,
        "active_province": state["last_active_province"],
        "batch_size": state["batch_size"],
        "candidate_cooldown_seconds": state["candidate_cooldown_seconds"],
        "provider_retry_cooldown_seconds": state["provider_retry_cooldown_seconds"],
        "single_cycle_timeout_seconds": state["single_cycle_timeout_seconds"],
        "idle_stop_seconds": state["idle_stop_seconds"],
        "max_run_seconds": state["max_run_seconds"],
        "provider_probe_timeout_seconds": state["provider_probe_timeout_seconds"],
        "province_switch_seconds": state["province_switch_seconds"],
        "run_started_at": state["run_started_at"],
        "last_unique_qualified_at": state["last_unique_qualified_at"],
    }


def finish_run(stop_reason: str) -> dict[str, Any]:
    state = load_state()
    provinces = list(state.get("province_order", []))
    run_started_at = parse_utc(state.get("run_started_at"))
    if provinces and run_started_at is not None:
        switch_seconds = max(int(state.get("province_switch_seconds", 1800)), 1)
        base_cursor = int(state.get("run_province_base_cursor", state.get("province_cursor", 0))) % len(provinces)
        elapsed_windows = int((datetime.now(timezone.utc) - run_started_at).total_seconds() // switch_seconds)
        next_cursor = (base_cursor + elapsed_windows + 1) % len(provinces)
        state["province_cursor"] = next_cursor
        state["last_active_province"] = provinces[(base_cursor + elapsed_windows) % len(provinces)]
    state["status"] = "stopped"
    state["run_finished_at"] = utc_now()
    state["last_stop_reason"] = stop_reason
    save_state(state)
    return {"ok": True, "state": state}


def stop_run() -> dict[str, Any]:
    return finish_run("stopped manually")


def complete_cycle(new_unique: int) -> dict[str, Any]:
    state = load_state()
    state["total_cycles"] = int(state.get("total_cycles", 0)) + 1
    active_province = compute_runtime_province(state)
    if active_province:
        state["last_active_province"] = active_province
    if new_unique > 0:
        state["total_new_unique"] = int(state.get("total_new_unique", 0)) + new_unique
        state["last_unique_qualified_at"] = utc_now()
    save_state(state)
    return {"ok": True, "state": state}


def update_provider_probes(results: list[dict[str, Any]]) -> dict[str, Any]:
    state = load_state()
    state["last_provider_probe_results"] = results
    save_state(state)
    return {"ok": True, "state": state}


def status() -> dict[str, Any]:
    ensure_dirs()
    state = load_state()
    active_province = compute_runtime_province(state)
    remaining_run_seconds = compute_remaining_run_seconds(state)
    remaining_province_window_seconds = compute_remaining_province_window_seconds(state)
    if active_province:
        state["last_active_province"] = active_province
        save_state(state)
    return {
        "ok": True,
        "data_root": str(DATA_ROOT),
        "index_path": str(INDEX_PATH),
        "state": state,
        "active_province": active_province,
        "remaining_run_seconds": remaining_run_seconds,
        "remaining_province_window_seconds": remaining_province_window_seconds,
        "registered_count": len({k for k in load_index().get("records", {}).keys() if "instagram.com/" not in k}),
    }


def export_pending(fmt: str, output: str | None) -> dict[str, Any]:
    ensure_dirs()
    pending = load_pending()
    items = pending.get("items", [])
    output_path = Path(output).expanduser().resolve() if output else EXPORTS_DIR / f"pending_submissions.{fmt if fmt != 'markdown' else 'md'}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        write_json(output_path, items)
    elif fmt == "csv":
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["creator_name", "profile_url", "followers"])
            writer.writeheader()
            for item in items:
                writer.writerow(
                    {
                        "creator_name": item.get("creator_name", ""),
                        "profile_url": item.get("profile_url", ""),
                        "followers": item.get("followers", ""),
                    }
                )
    else:
        lines = ["| Creator Name | Profile URL | Followers |", "| --- | --- | --- |"]
        for item in items:
            lines.append(
                f"| {item.get('creator_name', '')} | {item.get('profile_url', '')} | {item.get('followers', '')} |"
            )
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "output": str(output_path), "count": len(items), "format": fmt}


def main() -> int:
    ensure_dirs()
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("start-run")
    finish = sub.add_parser("finish-run")
    finish.add_argument("--stop-reason", required=True)
    sub.add_parser("stop-run")
    sub.add_parser("status")
    complete = sub.add_parser("complete-cycle")
    complete.add_argument("--new-unique", type=int, required=True)
    probes = sub.add_parser("update-provider-probes")
    probes.add_argument("--payload", required=True)

    uq = sub.add_parser("upsert-qualified")
    uq.add_argument("--payload", required=True)

    rr = sub.add_parser("record-review")
    rr.add_argument("--payload", required=True)

    export = sub.add_parser("export")
    export.add_argument("--format", choices=["markdown", "csv", "json"], default="markdown")
    export.add_argument("--output")

    args = parser.parse_args()
    try:
        if args.command == "start-run":
            result = start_run()
        elif args.command == "finish-run":
            result = finish_run(args.stop_reason)
        elif args.command == "stop-run":
            result = stop_run()
        elif args.command == "status":
            result = status()
        elif args.command == "complete-cycle":
            result = complete_cycle(args.new_unique)
        elif args.command == "update-provider-probes":
            payload = read_json(Path(args.payload), [])
            if not isinstance(payload, list):
                raise ValueError("probe payload must be a JSON list")
            result = update_provider_probes(payload)
        elif args.command == "upsert-qualified":
            payload = load_payload(Path(args.payload))
            validate_payload(payload)
            result = upsert_qualified(payload)
        elif args.command == "record-review":
            payload = load_payload(Path(args.payload))
            validate_payload(payload)
            result = record_review(payload)
        else:
            result = export_pending(args.format, args.output)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
