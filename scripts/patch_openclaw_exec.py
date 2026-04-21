#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path


def ensure_list(value):
    if isinstance(value, list):
        return value
    return []


def ensure_runtime_agent(config, target_root, runtime_agent_id):
    agents = config.get("agents")
    if not isinstance(agents, dict):
        agents = {}
        config["agents"] = agents

    agent_list = agents.get("list")
    if not isinstance(agent_list, list):
        agent_list = []
        agents["list"] = agent_list

    for agent in agent_list:
        if isinstance(agent, dict) and (agent.get("id") == runtime_agent_id or agent.get("name") == runtime_agent_id):
            tools = agent.get("tools")
            if not isinstance(tools, dict):
                tools = {}
                agent["tools"] = tools
            also_allow = ensure_list(tools.get("alsoAllow"))
            if "exec" not in also_allow:
                also_allow.append("exec")
            tools["alsoAllow"] = also_allow
            if "profile" not in tools:
                tools["profile"] = "full"
            return runtime_agent_id

    workspace = Path(target_root).expanduser() / "workspace-workking-runtime"
    agent_dir = Path(target_root).expanduser() / "agents" / runtime_agent_id / "agent"
    workspace.mkdir(parents=True, exist_ok=True)
    agent_dir.mkdir(parents=True, exist_ok=True)
    agent_list.append(
        {
            "id": runtime_agent_id,
            "name": runtime_agent_id,
            "workspace": str(workspace),
            "agentDir": str(agent_dir),
            "tools": {
                "alsoAllow": ["exec"],
                "profile": "full",
            },
        }
    )
    return runtime_agent_id


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


def patch_all_agents_exec(config):
    agents = config.get("agents")
    if not isinstance(agents, dict):
        return False, []

    agent_list = agents.get("list")
    if not isinstance(agent_list, list):
        return False, []

    patched = []
    for agent in agent_list:
        if not isinstance(agent, dict):
            continue
        tools = agent.get("tools")
        if not isinstance(tools, dict):
            tools = {}
            agent["tools"] = tools
        also_allow = ensure_list(tools.get("alsoAllow"))
        if "exec" not in also_allow:
            also_allow.append("exec")
        tools["alsoAllow"] = also_allow
        if "profile" not in tools:
            tools["profile"] = "full"
        patched.append(agent.get("id") or agent.get("name") or "unknown")
    return True, patched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--agent-id", default="main")
    parser.add_argument("--runtime-agent-id", default="workking-runtime")
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

    _, patched_agents = patch_all_agents_exec(data)

    runtime_agent = ensure_runtime_agent(data, args.target_root, args.runtime_agent_id)

    updated = json.dumps(data, ensure_ascii=False, indent=2) + os.linesep
    config_path.write_text(updated, encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "configPath": str(config_path),
        "patchedAgent": target_name,
        "patchedAgents": patched_agents,
        "runtimeAgent": runtime_agent,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
