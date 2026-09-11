---
title: Observability and Incident Response
status: current
version: "2.0"
audience: backend, platform, support, agents
last_reviewed: 2026-09-01
---

# Observability and Incident Response

Observability answers five questions: **what failed, who was affected, where
the work stopped, whether retry is safe, and how recovery can be verified.** A
log that answers none of them is noise. Which log store this service has, and
the commands to read it, are in [`../custom/`](../custom/README.md).

## Structured events

Emit stable event names and fields for the request, job and provider lifecycle
rather than relying on prose search. Include timestamp, environment, subsystem,
operation, outcome, duration, and a safe correlation identifier.

For tenant-owned work include a **non-secret** tenant reference, and only when
the logging policy permits it.

**MUST NOT** log authentication headers, raw API keys, webhook signatures,
payment secrets, full sensitive payloads, or model and prompt content by
default. **Redaction happens before the line is written**, not before it is
read — a redacting log viewer protects nobody once the bytes are on disk.

**AVOID** logging the same exception at several layers unless each event adds a
distinct lifecycle fact. Three copies of one traceback make an incident look
like three.

## Know what your log retention actually is

**A log store with a retention window is not an event store.** Where server-side
evidence is only the container log, an exception that scrolled out of the window
is **gone** — there is no query language over it and no way to recover it.

Two rules follow, and they are the most practically important on this page:

- **Treat it as a constraint on how much a single line must carry.** If you
  cannot go back and join against another record, the line has to be
  self-sufficient: what operation, what outcome, which correlation id.
- **Never treat the absence of a log line as proof that nothing failed.** It is
  equally consistent with "it failed before logging was configured", "it was
  logged at a level nobody captures", and "it scrolled away". A zero means *I
  could not see*, until a control in the same query proves otherwise.

Where a durable, queryable event store does exist, know **what it covers**. A
store that receives client-side crashes says nothing about server-side ones, and
reading it as though it covered both produces a confident, wrong all-clear.

## Alerting is notification, not ownership

A standing health signal is worth having, but **alerting is not durable
incident ownership**. Two constraints:

- A failure in the alerting channel MUST NOT affect the request or job being
  observed. Telemetry is a side effect; it never gets to break the work.
- An alert that fires on a single bad sample trains people to ignore it. Alert
  on a sustained condition.

## Incident workflow

1. Define the **symptom**, the user impact, the first known time, and the
   affected runtime path — before opening any log.
2. Read the **smallest relevant window** of the most relevant log. Start narrow;
   widening is cheap, and starting wide buries the signal.
3. Correlate HTTP, job, provider and client evidence — without treating absence
   of logs as health.
4. **Separate containment from root-cause repair.** Say which one you are doing.
   Avoid destructive queue or database actions unless explicitly authorized.
5. Verify recovery through the **user contract** plus structured evidence, not
   through the absence of new errors.
6. Record a durable invariant or check only when it prevents recurrence.

**MUST NOT restart everything as a diagnostic experiment.** A restart also
destroys the in-memory state that would have explained the failure — it converts
a diagnosable incident into an unexplained one that will recur.

## Jobs and providers

Record enqueue, start, completion, retry, terminal failure, and the relevant
provider event identity — without sensitive content. An operator needs to
distinguish **queued, running, delayed, duplicate, reconciled and failed** work;
a single "job finished" line distinguishes none of them.

**A success log emitted before commit or before provider confirmation is
misleading.** It will be read as evidence the thing happened.

## Review checklist

- Can one failed workflow be traced across its entry points?
- Do logs distinguish an expected rejection or degradation from a defect?
- Are sensitive fields redacted **before** leaving the process?
- Does any success line get written before the state it claims is durable?
- Is there a safe verification and recovery path that does not require editing
  data by hand?
