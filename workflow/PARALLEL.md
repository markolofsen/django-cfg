# Parallel development

This is a reusable coordination contract for a project with several development agents.
The agents may belong to different AI sessions or systems. CMDOP MCP supplies access to
the project machine; it does not assign tasks, select reviewers or merge changes.

## Roles and ownership

- One integration lead owns the canonical checkout (normally main), CURRENT, shared
  runtime, dependency and migration changes, final acceptance, and authorized publication.
- Each writing worker owns one task ID, actor ID, branch work/<task-id>, independent
  local checkout, exact base revision and disjoint writable paths.
- Reviewers read the actual changes and evidence. A reviewer does not acquire write
  ownership just by reviewing. Use the executing AI system's own native delegation when
  available; never invent delegated reviews or task results.
- Agree on contracts and dependencies before splitting work. Backend schema, generated
  clients, shared dependencies and migrations are not independent when they touch the
  same contract. Integrate the shared change first or serialize overlapping tasks.

Always run workflow commands from the integration Git root, or invoke the scripts in
that root by absolute path. A copied workflow inside a lane has its own local state;
do not use that copy to register a second integration queue.

## 1. Inspect and allocate

Run:

    python3 workflow/coord.py status
    python3 workflow/lanes.py status

Read AGENTS.md and workflow/CURRENT.md. The actual Git HEAD, active claim, registered
lane scopes and observed checkout state are authoritative. An old timestamp, stopped
process or missing result does not grant ownership.

From the integration root, use the observed full HEAD and actual project-relative
paths. The following is an example; replace the path with an existing component
or intended new file and provide the exact observed revision:

    python3 workflow/lanes.py open --id feature-api --actor backend-worker \
      --expected-head FULL_HEAD --path backend/component/ \
      --goal "Implement the agreed API contract"

Repeat --path for additional owned files/directories. A trailing slash means a
directory scope. Overlapping reservations and active integration claims are refused.
Lane creation reserves ownership before cloning; an interrupted creation is retained
for reconciliation, not silently retried.

The result gives branch and checkout. Work only in runtime/lanes/<task-id>. Each lane
is an independent local Git clone with its own .git directory, not a host-specific
linked worktree. Relative checkout paths work from the host and its mounted
container. No ignored environment file, runtime data, machine identity or remote
configuration is copied. Only committed source/history is cloned; secrets must never
be committed to the source repository.

## 2. Implement and report

Inspect the assigned checkout and base. Edit only the reserved paths. Use actual
tests/checks and record failures rather than guessing. Commit explicit owned files
on work/<task-id>; do not use a shared main checkout, reset other branches, force-push
or rewrite reviewed history. A task lane is linear and every introduced commit is
checked against its declared path scope, including changes later reverted.

Keep shared Docker Compose operations, live database migrations, dependency installation
and final browser sessions under one integration owner. Independent builds need their
own explicitly authorized resources and bounded concurrency. A lane source clone does
not create another running application, dependency cache, database or machine identity.
The shared application continues to use the integration checkout.

Return to the integration root and submit the exact committed SHA:

    python3 workflow/lanes.py submit --id feature-api --actor backend-worker \
      --commit FULL_LANE_SHA --evidence "Implemented contract; scoped tests passed; review the retained test receipt"

The queue records actor, goal, base, branch, commit, changed paths, submissions,
evidence and state. Evidence is a concise owner-reported summary, not automatic proof
that tests ran. For longer findings keep a task-specific report under an explicitly
owned path or a private receipt and reference it in the summary. Record dependency
changes, interface decisions, actual check outcomes, any real retained job IDs and
remaining blockers. Do not place secrets or customer data in reports.

States: creating, active, blocked, ready, integrated, abandoned. status also observes
missing or changed checkouts, wrong branch, dirty source and active local claims.
Use block with the task ID, actor and reason to record a blocker. A blocked task keeps
its reservation. Only its owner may reopen it with a reason after reconciliation;
the prior submissions remain. An integration claim prevents concurrent reopening.
abandon is an explicit owner decision on a clean, resolved lane and preserves its
checkout/history; it is not a deletion or a way to steal another agent's scope.
Never automatically expire an unresolved claim. If using coord.py for retained
jobs inside a lane, resolve them and finish that local claim before submitting.

Optional provider delivery: the repository owner configures the actual authorized
remote and protected branch policy. Lanes start without remotes or credentials.
The ordinary provider workflow can publish a checked task branch, not main. If an
authorized branch push already occurred, add --remote origin to submit (use the
actual approved remote name); it checks matching remote configuration and reads
the exact branch SHA. A local ready receipt without remote readback is not a push.
Do not push unchecked history or bypass a denied provider action.

## 3. Review and integrate

The integration lead reads the queue and actual task evidence, checks the latest
canonical branch, and reserves the ready lane using its full path scope. Use the
current HEAD and CURRENT digest from status, not a guessed or stale value:

    python3 workflow/coord.py begin --actor integration-lead --step merge-feature-api \
      --integration-lane feature-api --expected-head FULL_HEAD \
      --expected-current CURRENT_SHA256 --path backend/component/ \
      --path workflow/CURRENT.md

The result contains the real pass ID. Do not include another lane's reserved paths.
Import the reviewed commit:

    python3 workflow/lanes.py import --id feature-api --pass-id PASS_ID

This verifies the ready receipt, unchanged lane HEAD, branch, clean tree, complete
task history, exact base, active local claim absence and optional remote readback;
it fetches that exact commit into the integration repository. It never merges it.

Review the actual diff and affected contracts. If accepted, use ordinary Git to merge
the exact commit into the integration branch. For a clean, owned local checkout:

    git merge --no-ff --no-commit FULL_LANE_SHA

Run combined acceptance on the proposed result, reconcile any conflicts within the
claim, and commit the reviewed merge. The approved Git provider path may instead
require a PR/MR retaining the exact submitted commit in main ancestry. Observe and
read back the actual result; do not bypass provider protection. Squash or rebase that
changes the submitted SHA does not satisfy this exact-ancestry receipt.

Before release of the integration claim, record the next task in CURRENT and commit
only the declared changes. Resolve every retained job. Then:

    python3 workflow/coord.py finish --pass-id PASS_ID --outcome ready \
      --next-step "Next authorized task" --evidence "Exact lane SHA integrated; combined checks and evidence reviewed"

A successful finish checks the clean integration branch, allowed changes and exact
lane ancestry; it retains the integration receipt and marks the lane integrated.
The scripts do not run application tests or certify the reported evidence. If review
fails, preserve the claim while any merge or job remains unresolved; reconcile only
your own merge attempt, return a clean blocked handoff and have the lane owner reopen
the task if corrections are needed. Never silently replace a submitted commit.

Local integration, remote branch readback, actual remote main publication and
production deployment are separate outcomes. Only the authorized integration lead
or provider process may publish main. Verify the actual remote SHA after publication.
Do not deploy merely because a lane is integrated.

## Limits and distribution

Requires a real Git root with a committed workflow/CURRENT.md, workflow/coord.py,
workflow/lanes.py and ignored runtime/ and Python cache paths. Both the host and the
mounted workspace use the same integration checkout and private state directory.
The coordinator is a cooperative engineering contract, not an OS-level sandbox,
credential broker, automatic merge bot, scheduler or permission system. Provider
protected branches and scoped credentials remain necessary for untrusted contributors.

The reusable files belong in the customer distribution at its actual integration Git
root, with a clean initial cursor and customer-facing AGENTS entry. Never export an
existing internal CURRENT, actor registry, private runtime, credentials or retained
engineering evidence. Verify the generated tree and a fresh deployment separately.
