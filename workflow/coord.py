"""Host-side engineering handoff coordination; no Docker or scheduler mutations.

An existing claim is never expired automatically. The coordinator serializes
metadata, not arbitrary editors; contributors must use the same contract.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}$")
PROTECTED = {".git", ".env", ".secrets", "runtime", "vendor", "references", "machine-home"}
LANE_STATES = {"creating", "active", "blocked", "ready", "integrated", "abandoned"}


def now():
    return datetime.now(timezone.utc).isoformat()


def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                       text=True, timeout=20)
    if p.returncode:
        raise ValueError("Git preflight failed: " + " ".join(args[:2]))
    return p.stdout


def source_state(root):
    raw = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
              "--no-renames")
    dirty = sorted(x[3:] for x in raw.split("\0") if x)
    return {"head": git(root, "rev-parse", "HEAD").strip(),
            "branch": git(root, "branch", "--show-current").strip(),
            "current_sha256": hashlib.sha256(
                (root / "workflow/CURRENT.md").read_bytes()).hexdigest(),
            "dirty_paths": dirty}


def scope_path(value):
    stripped = value.rstrip("/")
    p = PurePosixPath(stripped)
    if (not stripped or p.is_absolute() or ".." in p.parts or not p.parts or
            p.parts[0] in PROTECTED or any(part.startswith(".env") or part in {".git", ".secrets"} for part in p.parts)
            or "\\" in value or p.as_posix() != stripped or any(ord(ch) < 32 for ch in value)):
        raise ValueError("Unsafe engineering scope path")
    return stripped + ("/" if value.endswith("/") else "")


def in_scope(name, paths):
    return any(name == p or (p.endswith("/") and name.startswith(p)) for p in paths)


def scopes_overlap(left, right):
    a, b = left.rstrip("/"), right.rstrip("/")
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def covers(scope, child):
    return scope == child or (scope.endswith("/") and child.startswith(scope))


def lane_dir(d):
    folder = d / "lanes"
    if folder.is_symlink():
        raise ValueError("Symlinked lane registry refused")
    folder.mkdir(exist_ok=True, mode=0o700)
    return folder


def lane_records(d):
    folder = lane_dir(d)
    records = []
    for path in sorted(folder.iterdir()):
        if path.suffix != ".json":
            continue
        if (not path.is_file() or path.is_symlink() or path.stat().st_size > 256_000
                or not SAFE_ID.fullmatch(path.stem)):
            raise ValueError("Invalid lane registry entry; reconcile before editing")
        item = read(path)
        if (not isinstance(item, dict) or item.get("schema_version") != 1
                or item.get("id") != path.stem or item.get("state") not in LANE_STATES
                or not isinstance(item.get("paths"), list) or not item["paths"]
                or any(not isinstance(x, str) or scope_path(x) != x for x in item["paths"])):
            raise ValueError("Invalid lane receipt; reconcile before editing")
        records.append(item)
    return records


def clean_text(value, limit=400):
    if not value or len(value) > limit or any(ord(ch) < 32 for ch in value):
        raise ValueError("Provide a short, non-secret single-line receipt")
    return value


def read(path):
    if path.is_symlink():
        raise ValueError("Symlinked coordination metadata refused")
    return json.loads(path.read_text()) if path.exists() else None


def write(path, value, exclusive=False):
    if path.is_symlink():
        raise ValueError("Symlinked coordination metadata refused")
    if exclusive:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        return
    fd, name = tempfile.mkstemp(prefix="." + path.name + "-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(root):
    root = Path(root).resolve()
    for folder in (root / "runtime", root / "runtime/workflow",
                   root / "runtime/workflow/results"):
        if folder.is_symlink():
            raise ValueError("Symlinked coordination directory refused")
        folder.mkdir(exist_ok=True, mode=0o700)
    d = root / "runtime/workflow"
    fd = os.open(d / ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield d


def status(root):
    root = Path(root).resolve()
    with locked(root) as d:
        claim = read(d / "claim.json")
        return {"source": source_state(root), "claim": claim,
                "lanes": [{k: item.get(k) for k in ("id", "actor", "state", "branch", "commit")}
                          for item in lane_records(d)],
                "last_result": read(d / "last-result.json"),
                "can_resume_automatically": False if claim else None,
                "note": "No claim expiry; empty claim alone does not authorize work."}


def begin(root, actor, step, paths, expected_head, expected_current,
          adopt_dirty=False, reviewers=(), integration_lane=None):
    root = Path(root).resolve()
    if not SAFE_ID.fullmatch(actor) or not SAFE_ID.fullmatch(step):
        raise ValueError("Invalid actor or stable step ID")
    paths = sorted(set(scope_path(p) for p in paths))
    if not paths:
        raise ValueError("Declare the exact owned files or directory prefixes")
    reviewers = [clean_text(x, 100) for x in reviewers]
    with locked(root) as d:
        if read(d / "claim.json"):
            raise ValueError("Another engineering claim exists; observe, never steal")
        src = source_state(root)
        if src["head"] != expected_head or src["current_sha256"] != expected_current:
            raise ValueError("Source or CURRENT changed after inspection; reread")
        if not src["branch"]:
            raise ValueError("An owning branch is required")
        if src["dirty_paths"]:
            if not adopt_dirty:
                raise ValueError("Dirty source requires explicit interactive ownership reconciliation")
            if any(not in_scope(n, paths) for n in src["dirty_paths"]):
                raise ValueError("Dirty paths outside declared ownership")
        lanes = lane_records(d)
        selected = None
        if integration_lane is not None:
            selected = next((x for x in lanes if x["id"] == integration_lane), None)
            if (selected is None or selected["state"] != "ready"
                    or selected.get("integration_branch") != src["branch"]
                    or not re.fullmatch(r"[0-9a-f]{40,64}", selected.get("commit", ""))):
                raise ValueError("Integration requires a ready lane for this branch")
            if not all(any(covers(p, child) for p in paths) for child in selected["paths"]):
                raise ValueError("Integration claim must cover the lane's reserved paths")
        for lane in lanes:
            if lane["state"] in {"integrated", "abandoned"} or lane["id"] == integration_lane:
                continue
            if any(scopes_overlap(a, b) for a in paths for b in lane["paths"]):
                raise ValueError("Scope overlaps reserved lane " + lane["id"])
        claim = {"schema_version": 1, "pass_id": uuid.uuid4().hex,
                 "actor": actor, "step": step, "state": "active",
                 "started_at_utc": now(), "heartbeat_at_utc": now(),
                 "base": src, "paths": paths,
                 "read_only_reviewers": reviewers,
                 "adopted_known_dirty": bool(src["dirty_paths"]),
                 "jobs": []}
        if selected is not None:
            claim.update(integration_lane=selected["id"], integration_commit=selected["commit"])
        write(d / "claim.json", claim, exclusive=True)
        return claim


def owned(d, pass_id):
    claim = read(d / "claim.json")
    if not claim or claim.get("pass_id") != pass_id:
        raise ValueError("No matching owner claim")
    return claim


def heartbeat(root, pass_id):
    with locked(root) as d:
        c = owned(d, pass_id)
        c["heartbeat_at_utc"] = now()
        write(d / "claim.json", c)
        return c


def record_job(root, pass_id, machine, task, purpose):
    if not SAFE_ID.fullmatch(machine) and not (
            1 <= len(machine) <= 80 and re.fullmatch(r"[A-Za-z0-9 ._-]+", machine)):
        raise ValueError("Invalid machine name")
    if task < 0:
        raise ValueError("Record the real CMDOP task ID")
    purpose = clean_text(purpose)
    with locked(root) as d:
        c = owned(d, pass_id)
        if any(x["machine"] == machine and x["task"] == task for x in c["jobs"]):
            raise ValueError("Task already recorded; reconcile instead of starting twice")
        c["jobs"].append({"machine": machine, "task": task, "purpose": purpose,
                          "state": "unreconciled", "recorded_at_utc": now()})
        c["heartbeat_at_utc"] = now()
        write(d / "claim.json", c)
        return c


def resolve_job(root, pass_id, machine, task, outcome, evidence):
    if outcome not in ("completed", "failed", "cancelled"):
        raise ValueError("Terminal job outcome required")
    evidence = clean_text(evidence)
    with locked(root) as d:
        c = owned(d, pass_id)
        matches = [x for x in c["jobs"] if x["machine"] == machine and x["task"] == task]
        if len(matches) != 1 or matches[0]["state"] != "unreconciled":
            raise ValueError("No matching unresolved task")
        matches[0].update(state=outcome, evidence=evidence, resolved_at_utc=now())
        c["heartbeat_at_utc"] = now()
        write(d / "claim.json", c)
        return c


def finish(root, pass_id, outcome, next_step, evidence):
    root = Path(root).resolve()
    if outcome not in ("ready", "blocked"):
        raise ValueError("Handoff must be ready or blocked")
    next_step = clean_text(next_step)
    evidence = clean_text(evidence)
    with locked(root) as d:
        c = owned(d, pass_id)
        if any(x["state"] == "unreconciled" for x in c["jobs"]):
            raise ValueError("Retained task outcome unknown; preserve the claim")
        src = source_state(root)
        if src["dirty_paths"]:
            raise ValueError("Commit or reconcile owned edits before releasing claim")
        if src["branch"] != c["base"]["branch"]:
            raise ValueError("Owning branch changed; preserve claim")
        p = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                            c["base"]["head"], src["head"]], capture_output=True, timeout=20)
        if p.returncode:
            raise ValueError("History changed; preserve claim")
        changed = [x for x in git(root, "diff", "--name-only", "--no-renames", "-z",
                                  c["base"]["head"], src["head"]).split("\0") if x]
        if any(not in_scope(n, c["paths"]) for n in changed):
            raise ValueError("Commits contain paths outside declared ownership")
        result = {"schema_version": 1, "pass_id": pass_id, "actor": c["actor"],
                  "step": c["step"], "outcome": outcome, "finished_at_utc": now(),
                  "base_head": c["base"]["head"], "source": src,
                  "changed_paths": sorted(changed), "jobs": c["jobs"],
                  "next_step": next_step, "evidence": evidence}
        lane = None
        if "integration_lane" in c:
            lane = next((x for x in lane_records(d) if x["id"] == c["integration_lane"]), None)
            if (lane is None or lane.get("commit") != c["integration_commit"]
                    or not (lane["state"] == "ready" or
                            (lane["state"] == "integrated" and lane.get("integration_pass_id") == pass_id))):
                raise ValueError("Integration lane receipt changed; reconcile before release")
            result.update(integration_lane=lane["id"], integration_commit=lane["commit"])
            if outcome == "ready":
                merged = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                                         lane["commit"], src["head"]], capture_output=True, timeout=20)
                if merged.returncode:
                    raise ValueError("Exact reviewed lane commit is not in the integration branch")
        saved = d / "results" / (pass_id + ".json")
        prior = read(saved)
        if prior:
            # A previous finish may have saved the result before releasing its
            # claim. Never overwrite that immutable result; reconcile exact state.
            for key in ("pass_id", "actor", "source", "outcome", "next_step", "evidence", "jobs",
                        "integration_lane", "integration_commit"):
                if prior.get(key) != result.get(key):
                    raise ValueError("Prior handoff differs; reconcile before release")
            result = prior
        else:
            write(saved, result, exclusive=True)
        write(d / "last-result.json", result)
        if lane is not None and outcome == "ready":
            if lane["state"] != "integrated":
                lane.update(state="integrated", integration_pass_id=pass_id,
                            integrated_head=src["head"], integrated_at_utc=now(),
                            integration_evidence=evidence)
                write(lane_dir(d) / (lane["id"] + ".json"), lane)
            elif lane.get("integrated_head") != src["head"]:
                raise ValueError("Prior integration receipt differs")
        (d / "claim.json").unlink()
        return result



def checkpoint_folder(d):
    folder = d / "checkpoints"
    if folder.is_symlink():
        raise ValueError("Symlinked checkpoint registry refused")
    folder.mkdir(exist_ok=True, mode=0o700)
    return folder


def receipt_records(folder, pattern, pass_id=None):
    """Read only typed receipts, never follow links or accept arbitrary files."""
    if folder.is_symlink():
        raise ValueError("Invalid receipt registry")
    if not folder.exists():
        return []
    if not folder.is_dir():
        raise ValueError("Invalid receipt registry")
    records = []
    for path in folder.iterdir():
        if path.suffix != ".json":
            continue
        match = re.fullmatch(pattern, path.name)
        if not match:
            raise ValueError("Unexpected receipt filename; reconcile before continuing")
        if pass_id is not None and match.group(1) != pass_id:
            continue
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
            raise ValueError("Invalid receipt file; reconcile before continuing")
        item = read(path)
        if (not isinstance(item, dict) or item.get("schema_version") != 1
                or item.get("pass_id") != match.group(1)):
            raise ValueError("Invalid receipt identity; reconcile before continuing")
        if pattern == CHECKPOINT_PATTERN:
            if (item.get("kind") != "checkpoint" or
                    item.get("checkpoint_id") != match.group(2) or
                    not isinstance(item.get("created_at_utc"), str) or
                    not isinstance(item.get("source"), dict) or
                    not isinstance(item.get("jobs"), list)):
                raise ValueError("Invalid checkpoint receipt; reconcile before continuing")
        elif not isinstance(item.get("finished_at_utc"), str):
            raise ValueError("Invalid terminal receipt; reconcile before continuing")
        records.append(item)
    return records


CHECKPOINT_PATTERN = r"([0-9a-f]{32})-([0-9a-f]{32})\.json"
RESULT_PATTERN = r"([0-9a-f]{32})\.json"


def checkpoint(root, pass_id, summary, next_step, evidence, blockers=()):
    """Save an immutable mid-pass snapshot without granting or releasing ownership."""
    summary, next_step, evidence = map(clean_text, (summary, next_step, evidence))
    blockers = [clean_text(x) for x in blockers]
    if len(blockers) > 16:
        raise ValueError("Summarize blockers in at most 16 entries")
    root = Path(root).resolve()
    with locked(root) as d:
        c = owned(d, pass_id)
        src = source_state(root)
        if src["branch"] != c["base"]["branch"]:
            raise ValueError("Owning branch changed; preserve claim")
        p = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                            c["base"]["head"], src["head"]], capture_output=True, timeout=20)
        if p.returncode:
            raise ValueError("History changed; preserve claim")
        changed = [x for x in git(root, "diff", "--name-only", "--no-renames", "-z",
                                  c["base"]["head"], src["head"]).split("\0") if x]
        if any(not in_scope(n, c["paths"]) for n in changed + src["dirty_paths"]):
            raise ValueError("Checkpoint includes paths outside declared ownership")
        checkpoint_id = uuid.uuid4().hex
        item = {"schema_version": 1, "kind": "checkpoint",
                "checkpoint_id": checkpoint_id, "pass_id": pass_id,
                "created_at_utc": now(), "source": src,
                "actor": c["actor"], "step": c["step"], "base": c["base"],
                "paths": c["paths"], "changed_paths": sorted(changed),
                "jobs": c["jobs"], "summary": summary, "next_step": next_step,
                "evidence": evidence, "blockers": blockers,
                "ownership": "active_claim_not_released"}
        folder = checkpoint_folder(d)
        write(folder / (pass_id + "-" + checkpoint_id + ".json"), item, exclusive=True)
        c["heartbeat_at_utc"] = now()
        write(d / "claim.json", c)
        return item


def resume(root):
    """Read a consistent transfer packet; this never authorizes or acquires a claim."""
    root = Path(root).resolve()
    with locked(root) as d:
        src = source_state(root)
        claim = read(d / "claim.json")
        last = read(d / "last-result.json")
        pass_id = (claim or last or {}).get("pass_id")
        snapshots = receipt_records(d / "checkpoints", CHECKPOINT_PATTERN, pass_id) if pass_id else []
        latest = max(snapshots, key=lambda x: (x["created_at_utc"], x["checkpoint_id"])) if snapshots else None
        if claim:
            disposition = "observe_active_claim"
        elif src["dirty_paths"]:
            disposition = "reconcile_dirty_source"
        elif not last:
            disposition = "no_terminal_handoff"
        elif last["source"] != src:
            disposition = "reconcile_source_drift"
        elif last["outcome"] == "blocked":
            disposition = "blocked_handoff"
        else:
            disposition = "review_ready_handoff"
        # A snapshot is historical evidence. Current Git, CURRENT and live job
        # receipts are authoritative, even if the snapshot is out of date.
        jobs = claim["jobs"] if claim else (last or {}).get("jobs", [])
        return {"schema_version": 1, "repository": str(root), "source": src,
                "current_path": "workflow/CURRENT.md",
                "current": (root / "workflow/CURRENT.md").read_text(),
                "disposition": disposition, "claim": claim, "last_result": last,
                "latest_checkpoint": latest,
                "checkpoint_matches_current_state": (
                    not src["dirty_paths"] and latest["source"] == src
                    and latest["jobs"] == jobs if latest else None),
                "unreconciled_jobs": [x for x in jobs if x["state"] == "unreconciled"],
                "lanes": [{k: x.get(k) for k in ("id", "actor", "state", "branch", "commit", "paths")}
                          for x in lane_records(d)],
                "note": "Read-only handoff; inspect real task outcomes, scope and owner authorization before begin. Never take over an active claim."}


def history(root, limit=20, pass_id=None):
    """Recent immutable mid-pass and terminal receipts (no live-state mutations)."""
    if not 1 <= limit <= 200:
        raise ValueError("History limit must be 1..200")
    if pass_id is not None and not re.fullmatch(r"[0-9a-f]{32}", pass_id):
        raise ValueError("Invalid pass ID")
    with locked(root) as d:
        rows = receipt_records(d / "checkpoints", CHECKPOINT_PATTERN, pass_id)
        rows += [dict(x, kind="terminal_result") for x in
                 receipt_records(d / "results", RESULT_PATTERN, pass_id)]
        rows.sort(key=lambda x: (x.get("finished_at_utc") or x["created_at_utc"],
                                 x.get("checkpoint_id", x["pass_id"])), reverse=True)
        return {"schema_version": 1, "total": len(rows), "receipts": rows[:limit]}


def mirror_status(root, remote, branch):
    """Compare committed source with a real remote branch without fetching or pushing."""
    root = Path(root).resolve()
    if not SAFE_ID.fullmatch(remote) or remote not in git(root, "remote").splitlines():
        raise ValueError("Configure the authorized Git remote first")
    ref = "refs/heads/" + branch
    valid = subprocess.run(["git", "check-ref-format", ref], capture_output=True, timeout=10)
    if valid.returncode or branch.startswith("-"):
        raise ValueError("Invalid remote branch")
    src = source_state(root)
    rows = git(root, "ls-remote", "--exit-code", "--heads", remote, ref).splitlines()
    if len(rows) != 1:
        raise ValueError("Require one exact remote branch readback")
    fields = rows[0].split()
    if len(fields) != 2 or fields[1] != ref or not re.fullmatch(r"[0-9a-f]{40,64}", fields[0]):
        raise ValueError("Unexpected Git remote readback")
    return {"source": src, "remote": remote, "remote_ref": ref,
            "remote_head": fields[0],
            "synchronized": src["head"] == fields[0] and not src["dirty_paths"],
            "note": "Source only; no runtime state, claims, credentials or identities synchronized."}


def main():
    parser = argparse.ArgumentParser(prog="python3 workflow/coord.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    p = sub.add_parser("mirror-status", help="Verify clean local source against a real remote branch")
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch", required=True)
    sub.add_parser("resume", help="Read the current transfer packet without claiming work")
    p = sub.add_parser("history", help="Read immutable intermediate and terminal receipts")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--pass-id")
    p = sub.add_parser("checkpoint", help="Save intermediate progress under an active claim")
    p.add_argument("--pass-id", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--next-step", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--blocker", action="append", default=[])
    p = sub.add_parser("begin")
    p.add_argument("--actor", required=True)
    p.add_argument("--step", required=True)
    p.add_argument("--path", action="append", required=True)
    p.add_argument("--expected-head", required=True)
    p.add_argument("--expected-current", required=True)
    p.add_argument("--adopt-dirty", action="store_true",
                   help="Interactive lead only; scheduled passes must never use")
    p.add_argument("--reviewer", action="append", default=[])
    p.add_argument("--integration-lane", help="Reserve a ready lane for explicit reviewed integration")
    for action in ("heartbeat", "record-job", "resolve-job", "finish"):
        p = sub.add_parser(action)
        p.add_argument("--pass-id", required=True)
        if action in ("record-job", "resolve-job"):
            p.add_argument("--machine", required=True)
            p.add_argument("--task", type=int, required=True)
        if action == "record-job":
            p.add_argument("--purpose", required=True)
        if action == "resolve-job":
            p.add_argument("--outcome", choices=["completed", "failed", "cancelled"], required=True)
            p.add_argument("--evidence", required=True)
        if action == "finish":
            p.add_argument("--outcome", choices=["ready", "blocked"], required=True)
            p.add_argument("--next-step", required=True)
            p.add_argument("--evidence", required=True)
    a = parser.parse_args()
    if a.command == "status":
        result = status(ROOT)
    elif a.command == "mirror-status":
        result = mirror_status(ROOT, a.remote, a.branch)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if not result["synchronized"]:
            raise SystemExit(3)
        return
    elif a.command == "resume":
        result = resume(ROOT)
    elif a.command == "history":
        result = history(ROOT, a.limit, a.pass_id)
    elif a.command == "checkpoint":
        result = checkpoint(ROOT, a.pass_id, a.summary, a.next_step, a.evidence, a.blocker)
    elif a.command == "begin":
        result = begin(ROOT, a.actor, a.step, a.path, a.expected_head,
                       a.expected_current, a.adopt_dirty, a.reviewer, a.integration_lane)
    elif a.command == "heartbeat":
        result = heartbeat(ROOT, a.pass_id)
    elif a.command == "record-job":
        result = record_job(ROOT, a.pass_id, a.machine, a.task, a.purpose)
    elif a.command == "resolve-job":
        result = resolve_job(ROOT, a.pass_id, a.machine, a.task, a.outcome, a.evidence)
    else:
        result = finish(ROOT, a.pass_id, a.outcome, a.next_step, a.evidence)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Workflow coordination refused: " + str(error), file=sys.stderr)
        raise SystemExit(2)
