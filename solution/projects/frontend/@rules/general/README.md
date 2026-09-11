---
title: General Frontend Standard — index
status: current
version: "1.0"
audience: product, design, frontend, agents
last_reviewed: 2026-09-01
---

# `general/` — the shared standard

Rules that hold in **every** frontend of this organisation, whatever the
framework. They are copied byte-for-byte between repositories, so a page here
must survive being read in a codebase that shares none of your dependencies.

**This directory has one source.** It is authored in the console frontend and
copied into every other frontend by a sync script; the repository profile names
the script and the source path. Edit the source; never patch a copy. A gate
compares them, because a copy that drifts is worse than a second file — it looks
authoritative and is quietly wrong. Nothing runs that gate on a schedule: it
fails when a person runs it, so a patched copy survives until the next manual
pass.

## Read by task

| Work | Page |
|---|---|
| **Any task, before starting** | [Working agreement](working-agreement.md) |
| A product or architecture decision | [Google and Apple principles](google-apple-product-principles.md) |
| Any feature or UX change | [Product UX](product-ux.md) |
| Planning a new feature end to end | [Feature workflow](feature-workflow.md) |
| Package and layer boundaries, one-owner questions | [Architecture and ownership](architecture-and-ownership.md) |
| Which folder, what name, when to split, barrels, dead code | [Code organization and naming](code-organization-and-naming.md) |
| Where a value lives, caches, live data, mutations | [State and data](state-and-data.md) |
| Telling one layer that something happened | [Events and notifications](events-and-notifications.md) |
| Adding an internal URL or a link | [Declarative routes and links](declarative-routes.md) |
| Routes, shell, master/detail, responsive | [Navigation and layout](navigation-layout-and-responsive.md) |
| Choosing or admitting a shared component | [Design system and reuse](design-system.md) |
| Forms, dialogs, component contracts | [Components and interactions](components-and-interactions.md) |
| Tokens, themes, programmatic colors | [Tokens, themes, and styles](tokens-themes-and-styles.md) |
| A class list that no longer reads, or a stylesheet to split | [Stylesheets and class lists](stylesheets-and-class-lists.md) |
| Copy, accessibility, locale, time formats | [Accessibility, content, and i18n](accessibility-content-and-i18n.md) |
| Types, `any`, boundaries, narrowing | [Typing and type safety](typing-and-type-safety.md) |
| Scenarios, interaction contracts, evidence | [Executable UI specifications](executable-ui-specifications.md) |
| Verifying a change, definition of done | [Delivery and verification](delivery-and-verification.md) |
| Comments and doc comments | [Comments and code narration](comments-and-code-narration.md) |
| Agent instructions, skills, delegation | [Agent-ready development](agent-ready-development.md) |

Read the **whole page**, not a match inside it. A search returns the lines that
agree with the phrasing you already had in mind and hides the clause that would
have changed what you did.

## What belongs here, and what does not

A page qualifies only if it stays true in a repository with a different
framework, different packages, and a different backend.

**Belongs:** the decision order, what a comment must carry, the accessibility
baseline, how to choose between a dialog and a route, what makes copy
actionable, how state is classified by how it arrives.

**Does not belong**, and is the recurring failure mode:

- A package, alias, or import path. `@acme/ui-core` means nothing next door.
- A command. `make ship`, `pnpm check:jsx-boundary`, the name of a gate script.
- A framework assumption. Server components, `go:embed`, a store library, a
  workbench that one repository has and another does not.
- A worked example built on a domain the other repository has never heard of.

Where a rule is universal but its *enforcement* is local, state the rule here
and let the repository profile in `custom/` name the command. "A gate SHOULD
enforce this" is portable; "`pnpm check:x` enforces this" is not.

**The test before adding a line:** would this sentence be *false* — not merely
irrelevant — in the sibling repository? If yes, it belongs in `custom/`.

## Why this directory exists

These pages previously lived twice, once per repository, with no link between
the copies. They drifted for two months in both directions: the same page ran
127 lines in one tree and 89 in the other, and neither was a subset of the
other. Worse, whole pages described a codebase that was not the one containing
them — a routing page whose worked example was a property-search product, a
specifications page devoted to a test runner the repository did not have.

A rule that describes the wrong codebase is not merely stale. It is followed,
and it produces code shaped for a system that does not exist.
