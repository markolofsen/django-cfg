---
title: Working Agreement
status: current
version: "1.0"
audience: agents
last_reviewed: 2026-09-01
---

# Working Agreement

How the repository owner expects an agent to communicate and operate. Every
other document here describes the product; this one describes the collaboration.
It applies to every task in this repository, including a task that touches no
code.

## Language

- Write **English** in every artifact: source, comments, doc comments, commit
  messages, Markdown, plans, and delivery notes. This holds regardless of the
  language the request arrived in.
- Reply to the owner in the language the owner used.

## Reading the request

The owner dictates by voice. Expect transcription artifacts — a misheard word, a
missing negation, a technical term rendered phonetically, punctuation that lands
in the wrong place.

- Read for **intent**, not for the literal token stream. A word that makes no
  sense in context is almost always a transcription error for a nearby word that
  does.
- A request that appears to contradict itself is more likely mis-transcribed than
  genuinely contradictory. Resolve it against the surrounding context, the code,
  and the task history.
- Ask only when two plausible readings lead to **materially different work**.
  Do not ask to confirm a reading you can settle by opening a file.

## Writing back

- Be **brief and specific**. State the outcome, the evidence, and what is still
  open.
- No preamble, no restatement of the request, no summary of what you are about
  to do, no closing offer to help further.
- Prefer the concrete noun to the category: name the file, the symbol, the
  command, the line. `route-registry.ts:41` beats "the routing layer".
- Report failures as plainly as successes. A skipped check is a result; a test
  that failed is a result. Never describe work as verified when it was not.

## Concurrent agents

Other agents work in this tree at the same time.

- A build failure, a red test, or a conflicted file **may belong to somebody
  else**. Establish whether your change caused it before treating it as your
  bug, and say which it is when you report.
- Transient breakage is not a reason to stop. Retry later and continue with work
  that does not depend on it.
- Never discard another agent's work to clean your own path: no `git stash`, no
  `git checkout <path>`, no branch reset, no blanket `git add -A`. Stage the
  paths you actually changed.
- Leave unrelated dirty files exactly as you found them.

## Delegation

Delegate a self-contained, one-off task to a subagent when its **research would
otherwise flood this context** — a broad search across many files, a mechanical
sweep, an independent review. Keep the conclusion; discard the file dumps.

Delegation does not transfer judgment. The result comes back as evidence to
check, not as a verdict to adopt: verify the claim against the source before
acting on it, and verify the edit yourself. See
[Agent-ready development](./agent-ready-development.md) for who runs which
verification command, and why a subagent must not run the slow ones.

## Where this sits

Engineering standards for the product live in
[Google and Apple product principles](./google-apple-product-principles.md) —
single source of truth, clear ownership, minimal coupling, and an interface that
needs no explanation. This page does not restate them; it governs the working
relationship around them.
