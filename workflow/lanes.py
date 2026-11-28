"""Cooperative branch lanes for agents sharing a development repository.

Uses the existing coordinator lock and local Git copies. No push, merge,
credential provisioning, Docker action or agent launch is performed here.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

import coord

ROOT = coord.ROOT
CONTROL = ("workflow/CURRENT.md", "workflow/coord.py", "workflow/lanes.py")
OID = re.compile(r"[0-9a-f]{40,64}")


def git(root, *args, timeout=30):
    result = subprocess.run(["git", "-C", str(root), *map(str, args)],
                            capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise ValueError("Lane Git check failed: " + " ".join(map(str, args[:2])))
    return result.stdout


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value):
    require(isinstance(value, str) and coord.SAFE_ID.fullmatch(value) and value not in {".", ".."},
            "Invalid lane or actor identifier")
    return value


def registry_entry(d, lane_id):
    identifier(lane_id)
    item = next((x for x in coord.lane_records(d) if x["id"] == lane_id), None)
    require(item is not None, "Unknown lane")
    return item


def save(d, item, exclusive=False):
    coord.write(coord.lane_dir(d) / (identifier(item["id"]) + ".json"), item, exclusive)


def checkout(root, lane_id):
    p = root / "runtime" / "lanes" / identifier(lane_id)
    for part in (p.parent.parent, p.parent, p):
        require(not part.is_symlink(), "Symlinked lane path refused")
    return p


def exact_root(root):
    root = Path(root).resolve()
    require(Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() == root,
            "Use the actual integration Git root")
    return root


def open_lane(root, lane_id, actor, expected_head, paths, goal):
    root = exact_root(root)
    identifier(lane_id)
    identifier(actor)
    git(root, "check-ref-format", "--branch", "work/" + lane_id)
    require(OID.fullmatch(expected_head), "Exact integration base SHA required")
    paths = sorted(set(coord.scope_path(p) for p in paths))
    require(paths, "Explicit lane scope required")
    require(not any(coord.scopes_overlap(p, k) for p in paths for k in CONTROL),
            "The integration cursor and coordinator belong to the integration lead")
    goal = coord.clean_text(goal)
    dest = checkout(root, lane_id)
    with coord.locked(root) as d:
        src = coord.source_state(root)
        require(src["head"] == expected_head and src["branch"], "Integration base changed")
        require(not any(coord.scopes_overlap(p, q) for p in paths for q in src["dirty_paths"]),
                "Lane overlaps uncommitted integration work")
        claim = coord.read(d / "claim.json")
        require(not claim or not any(coord.scopes_overlap(p, q) for p in paths for q in claim["paths"]),
                "Lane overlaps active integration claim")
        for item in coord.lane_records(d):
            require(item["id"] != lane_id, "Lane ID already exists; reconcile existing receipt")
            if item["state"] not in {"integrated", "abandoned"}:
                require(not any(coord.scopes_overlap(p, q) for p in paths for q in item["paths"]),
                        "Scope overlaps reserved lane " + item["id"])
        require(not dest.exists(), "Lane checkout already exists")
        ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "-q",
                                  str(dest.relative_to(root))], capture_output=True, timeout=10)
        require(ignored.returncode == 0, "Lane storage must be ignored by the integration repository")
        item = {"schema_version": 1, "id": lane_id, "actor": actor, "goal": goal,
                "paths": paths, "base": expected_head, "integration_branch": src["branch"],
                "branch": "work/" + lane_id, "checkout": "runtime/lanes/" + lane_id,
                "state": "creating", "created_at_utc": coord.now(), "submissions": []}
        save(d, item, exclusive=True)
    # Reservation survives interruption. No other owner can claim these paths.
    try:
        dest.parent.mkdir(mode=0o700, exist_ok=True)
        git(root, "clone", "--no-hardlinks", "--local", "--no-checkout", "--single-branch",
            "--branch", item["integration_branch"], "--", root, dest, timeout=120)
        git(dest, "switch", "-c", item["branch"], expected_head)
        git(dest, "remote", "remove", "origin")
        require(git(dest, "rev-parse", "HEAD").strip() == expected_head and
                not git(dest, "status", "--porcelain", "--untracked-files=all").strip(),
                "New lane checkout is not the exact clean base")
        require(not git(dest, "remote").strip(), "New lane must not inherit a remote")
    except (ValueError, OSError, subprocess.SubprocessError):
        # Preserve partial checkout and reservation for explicit reconciliation.
        with coord.locked(root) as d:
            item = registry_entry(d, lane_id)
            if item["state"] == "creating":
                item.update(state="blocked", blocker="Checkout preparation failed; inspect exact lane path")
                save(d, item)
        raise
    with coord.locked(root) as d:
        item = registry_entry(d, lane_id)
        require(item["state"] == "creating" and item["actor"] == actor,
                "Lane reservation changed during creation")
        item.update(state="active", updated_at_utc=coord.now())
        save(d, item)
        return item


def verify_lane(root, item, commit):
    dest = checkout(root, item["id"])
    require(dest.is_dir() and exact_root(dest) == dest.resolve(), "Missing independent lane checkout")
    require(OID.fullmatch(commit) and git(dest, "rev-parse", "HEAD").strip() == commit,
            "Lane HEAD differs from reported commit")
    require(git(dest, "branch", "--show-current").strip() == item["branch"],
            "Lane is not on its assigned branch")
    require(not git(dest, "status", "--porcelain", "--untracked-files=all").strip(),
            "Lane has uncommitted changes")
    require(coord.read(dest / "runtime/workflow/claim.json") is None,
            "Lane has an active local task claim; reconcile it first")
    # Check every introduced commit, not just the final diff. No hidden merge
    # histories or reverted out-of-scope commits in the review branch.
    git(dest, "merge-base", "--is-ancestor", item["base"], commit)
    commits = git(dest, "rev-list", "--reverse", item["base"] + ".." + commit).splitlines()
    require(0 < len(commits) <= 128, "Expected a bounded nonempty task history")
    require(not git(dest, "rev-list", "--merges", item["base"] + ".." + commit).strip(),
            "Task lane history must be linear; ask integrator to reconcile merges")
    changed = set()
    for sha in commits:
        paths = git(dest, "diff-tree", "--no-commit-id", "-r", "--name-only", "--no-renames",
                    "-z", sha).split("\0")
        for path in filter(None, paths):
            require(coord.in_scope(path, item["paths"]), "Lane commit outside reserved paths: " + path)
            changed.add(path)
    require(changed, "Lane has no source changes")
    return dest, sorted(changed)


def verify_remote(root, dest, item, remote, commit):
    identifier(remote)
    # Remote configuration belongs to the owner. Compare without displaying
    # URLs; this tool neither grants credentials nor sends a push.
    for args in (("remote", "get-url", "--all", remote),
                 ("remote", "get-url", "--push", "--all", remote)):
        require(git(root, *args).strip() == git(dest, *args).strip(),
                "Lane remote does not match integration repository")
    ref = "refs/heads/" + item["branch"]
    reply = git(dest, "ls-remote", "--exit-code", "--heads", remote, ref)
    require(reply.splitlines() == [commit + "\t" + ref], "Remote lane SHA differs from reviewed commit")
    return ref


def submit(root, lane_id, actor, commit, evidence, remote=None):
    root = exact_root(root)
    evidence = coord.clean_text(evidence)
    with coord.locked(root) as d:
        item = registry_entry(d, lane_id)
        require(item["actor"] == actor and item["state"] in {"active", "blocked"},
                "Only the active lane owner may submit")
        dest, paths = verify_lane(root, item, commit)
        ref = verify_remote(root, dest, item, remote, commit) if remote else None
        submission = {"commit": commit, "changed_paths": paths,
                      "verification": "owner_reported", "evidence": evidence,
                      "remote": remote, "remote_ref": ref,
                      "remote_verified_sha": commit if remote else None,
                      "submitted_at_utc": coord.now()}
        item["submissions"].append(submission)
        item.update(submission, state="ready")
        item.pop("blocker", None)
        save(d, item)
        return item


def transition(root, lane_id, actor, action, reason):
    root = exact_root(root)
    reason = coord.clean_text(reason)
    require(action in {"block", "reopen", "abandon"}, "Unknown lane transition")
    with coord.locked(root) as d:
        item = registry_entry(d, lane_id)
        require(item["actor"] == actor, "Wrong lane owner")
        claim = coord.read(d / "claim.json")
        require(not claim or claim.get("integration_lane") != lane_id,
                "Integration owner is reviewing this lane")
        if action == "block":
            require(item["state"] == "active", "Only active lane may be blocked")
            item.update(state="blocked", blocker=reason)
        elif action == "reopen":
            require(item["state"] in {"ready", "blocked"}, "Only ready/blocked lane may reopen")
            dest = checkout(root, lane_id)
            require(dest.is_dir() and exact_root(dest) == dest.resolve() and
                    git(dest, "branch", "--show-current").strip() == item["branch"],
                    "Reconcile lane checkout before reopening")
            item.update(state="active", reopen_reason=reason)
        else:
            require(item["state"] in {"active", "blocked", "ready"}, "Cannot abandon this lane state")
            dest = checkout(root, lane_id)
            require(dest.is_dir() and exact_root(dest) == dest.resolve() and
                    not git(dest, "status", "--porcelain", "--untracked-files=all").strip()
                    and coord.read(dest / "runtime/workflow/claim.json") is None,
                    "Preserve unresolved lane checkout and task claim")
            item.update(state="abandoned", abandon_reason=reason)
        item["updated_at_utc"] = coord.now()
        save(d, item)
        return item


def import_lane(root, lane_id, pass_id):
    root = exact_root(root)
    with coord.locked(root) as d:
        claim = coord.owned(d, pass_id)
        item = registry_entry(d, lane_id)
        require(claim.get("integration_lane") == lane_id and item["state"] == "ready"
                and claim.get("integration_commit") == item.get("commit"),
                "Acquire a matching integration claim first")
        src = coord.source_state(root)
        require(src["head"] == claim["base"]["head"] and not src["dirty_paths"],
                "Integration checkout changed; reconcile before import")
        require(src["branch"] == item["integration_branch"], "Wrong integration branch")
        git(root, "merge-base", "--is-ancestor", item["base"], src["head"])
        dest, paths = verify_lane(root, item, item["commit"])
        require(paths == item["changed_paths"], "Lane changed since submission")
        if item.get("remote"):
            verify_remote(root, dest, item, item["remote"], item["commit"])
        git(root, "fetch", "--no-tags", "--no-write-fetch-head", "--", dest, item["commit"], timeout=120)
        require(git(root, "cat-file", "-t", item["commit"]).strip() == "commit",
                "Exact reviewed object unavailable")
        return {"id": lane_id, "commit": item["commit"], "changed_paths": paths,
                "imported": True, "merged": False,
                "next": "Review exact commit; explicit merge and combined checks by integration owner"}


def status(root):
    root = exact_root(root)
    with coord.locked(root) as d:
        items = []
        for item in coord.lane_records(d):
            v = dict(item)
            dest = checkout(root, item["id"])
            try:
                if dest.is_dir() and exact_root(dest) == dest.resolve():
                    head = git(dest, "rev-parse", "HEAD").strip()
                    dirty = bool(git(dest, "status", "--porcelain", "--untracked-files=all").strip())
                    branch = git(dest, "branch", "--show-current").strip()
                    local_claim = coord.read(dest / "runtime/workflow/claim.json")
                    v["observed"] = {"head": head, "branch": branch, "dirty": dirty,
                                     "active_local_claim": bool(local_claim)}
                    if item["state"] == "ready" and (head != item.get("commit") or dirty
                            or branch != item["branch"] or local_claim):
                        v["observed_state"] = "drift"
                else:
                    v["observed_state"] = "missing_checkout"
            except (ValueError, OSError, subprocess.SubprocessError):
                v["observed_state"] = "unknown"
            items.append(v)
        return {"integration": coord.source_state(root), "claim": coord.read(d / "claim.json"),
                "lanes": items, "note": "Local integration is not remote main publication. No automatic merge or expiry."}


def main():
    import json
    parser = argparse.ArgumentParser(prog="python3 workflow/lanes.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    p = sub.add_parser("open")
    p.add_argument("--id", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--expected-head", required=True)
    p.add_argument("--path", action="append", required=True)
    p.add_argument("--goal", required=True)
    p = sub.add_parser("submit")
    p.add_argument("--id", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--remote")
    for action in ("block", "reopen", "abandon"):
        p = sub.add_parser(action)
        p.add_argument("--id", required=True)
        p.add_argument("--actor", required=True)
        p.add_argument("--reason", required=True)
    p = sub.add_parser("import")
    p.add_argument("--id", required=True)
    p.add_argument("--pass-id", required=True)
    a = parser.parse_args()
    if a.command == "status":
        result = status(ROOT)
    elif a.command == "open":
        result = open_lane(ROOT, a.id, a.actor, a.expected_head, a.path, a.goal)
    elif a.command == "submit":
        result = submit(ROOT, a.id, a.actor, a.commit, a.evidence, a.remote)
    elif a.command == "import":
        result = import_lane(ROOT, a.id, a.pass_id)
    else:
        result = transition(ROOT, a.id, a.actor, a.command, a.reason)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Lane coordination refused: " + str(error), file=sys.stderr)
        raise SystemExit(2)
