---
title: Delivery and Verification
status: current
version: "3.0"
audience: frontend, qa, platform, agents
last_reviewed: 2026-09-01
---

# Delivery and Verification

A green typecheck proves only that a subset of contracts compile. A frontend
change is done when the intended artifact runs and the changed workflow has been
observed in a real browser.

## Verification ladder

Run the cheapest relevant checks first:

1. Pure unit tests for state transitions, formatters, and view-model derivation.
2. Package typecheck and lint.
3. Component/scenario tests for visible states and interaction contracts.
4. App build to catch bundling, exports, CSS scanning, and lazy chunks.
5. Browser verification on every changed route and state.
6. End-to-end integration for auth, transport, persistence, and destructive
   workflows.
7. Embedded/native artifact verification when the product ships one.

Do not repeatedly run the slowest build while resolving local type errors.
Use the scenario and evidence contracts in
[Executable UI specifications](./executable-ui-specifications.md) for material
interface changes.

## Browser evidence

For each changed flow verify:

- no new console errors or unhandled rejections;
- correct route, back/forward, reload, and direct-entry behavior;
- for auth changes, verify first load, normal reload, hard reload, logout, and
  recovery from a stale or missing browser session;
- initial loading, empty, ready, stale/revalidating, error, and unavailable;
- primary mutation success, double-submit prevention, and failure recovery;
- keyboard traversal, focus restoration, and visible focus;
- narrow and wide layouts;
- light and dark modes;
- long content or translated strings when copy/layout changed;
- reconnect/offline behavior when network state is relevant.

Screenshots support review but do not replace interaction evidence.

## Accessibility checks

Combine:

- semantic/ARIA inspection;
- keyboard-only walkthrough;
- automated axe or equivalent scan;
- zoom and text scaling;
- reduced motion;
- a screen-reader spot check for novel interactions.

Automated checks cannot prove correct focus order, useful names, or understandable
error recovery.

## Performance checks

Use measurement proportional to risk:

- Inspect route chunk changes when adding a heavy dependency.
- Lazy-load editors, syntax highlighters, charts, and viewers when not needed at
  first paint.
- Check rerenders before adding memoization.
- Reserve geometry for lazy content and media.
- Profile long lists; virtualize only when data size warrants it.
- Test on a production build because dev mode changes React and bundler costs.

For user-facing web routes, target good Core Web Vitals: LCP under 2.5 seconds,
INP under 200 milliseconds, and CLS under 0.1 at the 75th percentile.

## Security and privacy checks

- No secret in URL, DOM longer than needed, analytics, logs, screenshots, or
  persisted state.
- Auth configuration has one owner. A capability-level `401` triggers canonical
  session confirmation and bounded recovery; only the auth owner may transition
  the application to re-authentication.
- User-visible HTML/Markdown/code rendering is sanitized according to trust.
- File paths, downloads, and uploads enforce server-side authorization.
- Destructive mutations are protected against replay/double submit as required.
- Browser errors sent to telemetry are redacted.
- Permission-denied behavior does not reveal protected resource existence.

## Cross-repository and generated artifacts

- Rebuild a shared package if consumers read its `dist` output.
- Sync it through the supported copy workflow, not a symlink.
- Restart the dev server or clear its dependency cache after a source sync.
- Regenerate API/binding output from its source command.
- Verify the packaged/embedded asset, not merely the frontend `dist` directory.
- A local sync is temporary until the shared package is committed, versioned,
  published, and reinstalled by the consumer.

## Concurrent work and flaky environments

When another process or agent is editing/building:

- inspect the failing file and process before changing anything;
- preserve unrelated modifications;
- rerun a transient build after the competing writer finishes;
- report checks skipped because of external contention;
- never hide a reproducible failure as concurrency.

## Definition of done

- [ ] User-facing states and recovery are implemented.
- [ ] Relevant unit and package tests pass.
- [ ] Typecheck and lint pass for affected packages.
- [ ] Production build succeeds.
- [ ] Changed routes are browser-verified with no new console errors.
- [ ] Keyboard, responsive, light, and dark behavior are checked.
- [ ] Accessibility and security checks match the risk.
- [ ] Bundle/performance impact is understood.
- [ ] Generated, shared, embedded, or native artifacts are current.
- [ ] Documentation and screenshots/evidence are updated.

## Nothing here runs on a schedule

Every gate in this page's ladder fails only when a person runs it. There is no
automatic verification lane and there is not going to be one, so a check nobody
runs locally is a check that never runs. Two consequences:

- A green result is evidence only for the commands you actually invoked. Report
  which ones those were and which rungs you skipped.
- A gate that would have caught a rule is not a substitute for the rule. Until
  someone runs it, the rule is upheld by whoever is editing.

The repository profile names this repository's commands, gates, and known build
boundaries. Read it for the exact invocations; the ladder above is what they are
for.
