#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path


def ensure_list(value):
    if isinstance(value, list):
        return value
    return []


def patch_agent_exec(config, agent_id):
    agents = config.get("agents")
    if not isinstance(agents, dict):
        return False, f"missing agents block in {agent_id!r} config"

    agent_list = agents.get("list")
    if not isinstance(agent_list, list):
        return False, "missing agents.list"

    target = None
    if agent_id:
        for agent in agent_list:
            if isinstance(agent, dict) and (agent.get("id") == agent_id or agent.get("name") == agent_id):
                target = agent
                break
    if target is None and agent_list:
        first = agent_list[0]
        if isinstance(first, dict):
            target = first

    if target is None:
        return False, "no patchable agent found"

    tools = target.get("tools")
    if not isinstance(tools, dict):
        tools = {}
        target["tools"] = tools

    also_allow = ensure_list(tools.get("alsoAllow"))
    if "exec" not in also_allow:
        also_allow.append("exec")
    tools["alsoAllow"] = also_allow

    if "profile" not in tools:
        tools["profile"] = "full"

    return True, target.get("id") or target.get("name") or "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--agent-id", default="main")
    args = parser.parse_args()

    config_path = Path(args.target_root).expanduser() / "openclaw.json"
    if not config_path.exists():
        print(json.dumps({
            "ok": False,
            "reason": "config-missing",
            "configPath": str(config_path),
        }))
        return 0

    raw = config_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    changed, target_name = patch_agent_exec(data, args.agent_id)
    if not changed:
        print(json.dumps({
            "ok": False,
            "reason": target_name,
            "configPath": str(config_path),
        }))
        return 1

    updated = json.dumps(data, ensure_ascii=False, indent=2) + os.linesep
    config_path.write_text(updated, encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "configPath": str(config_path),
        "patchedAgent": target_name,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
