---
title: Design System and Reuse
status: current
version: "3.0"
audience: design, frontend, agents
last_reviewed: 2026-09-01
---

# Design System and Reuse

The design system is a product contract, not a component catalogue. It aligns
behavior, accessibility, tokens, and implementation across applications.

## Reuse order

Before creating UI, search in this order:

1. Existing product pattern with the same behavior.
2. A primitive or hook from the shared primitive library.
3. A domain-shaped surface from the shared composed-surface library.
4. Composition of existing primitives in the product UI package.
5. New product-specific component.
6. New shared-library component after proving cross-product value.

**The order is the rule.** Skipping a step does not merely duplicate code — it
duplicates a BEHAVIOR contract, so the two copies drift on keyboard handling and
ARIA rather than on appearance, where nobody looks.

## Library roles

Where the design system is split across packages, each has one job. Naming
varies; the split does not.

### The primitive library

Accessible primitives, layout parts, overlays, forms, feedback, navigation,
semantic tokens, the theme runtime, router adapters, and common hooks. This is
the first place to look and the layer product code depends on most.

### The composed-surface library

Expensive devtool and dashboard capabilities: chat, logs, data grids, code
editors, diffs, JSON views, charts, media, API viewers. These are heavy, so
they are normally reached through explicit subpath exports and lazy-loaded where
they are not needed at first paint.

**MUST**: verify the package's `exports` map before importing. A package may
have no root `"."` export at all, and a README example or a remembered import
path is not evidence — the exports map is. An import that does not resolve is
the cheap failure; one that resolves to a deep internal path is the expensive
one, because it keeps working until the package reorganises.

## Primitive, pattern, feature

| Level | Owns | Must not own |
|---|---|---|
| Primitive | semantics, keyboard behavior, ARIA, base variants | product workflow |
| Product pattern | repeatable composition and layout mechanics | a single feature's transport |
| Feature | product terms, data, permissions, workflow | global design tokens |

Examples:

- `Dialog` is a primitive.
- A responsive master/detail layout is a product pattern.
- An onboarding or enrollment flow is a feature.

Moving feature logic into a primitive makes the library harder to reuse.
Rebuilding primitive behavior inside a feature creates accessibility drift.

## Component admission test

Before adding to a shared package, answer yes to all relevant questions:

- Is the behavior repeated or clearly cross-product?
- Can its props be named without one feature's vocabulary?
- Can accessibility and responsive behavior be specified independently?
- Does central ownership reduce real maintenance cost?
- Can the component be tested and documented as a stable public contract?

If not, keep it local. Extraction is cheaper after the second concrete use than
repairing a premature abstraction.

## Composition rules

- Product code MUST use the shared `Button`/icon-button/link primitives when
  their contract fits. Do not hand-style a raw `<button>` for retry, refresh,
  copy, menu, dialog, or destructive actions.
- A raw native control is allowed only when the shared system cannot express a
  required platform semantic; document that exception beside the code.
- Prefer slots and semantic subcomponents over many boolean props.
- Keep controlled and uncontrolled APIs deliberate; do not mix them silently.
- Forward refs and native attributes when the primitive contract requires it.
- Preserve native semantics. A link navigates; a button performs an action.
- Variants describe product semantics (`destructive`, `warning`, `quiet`) rather
  than one screen's color.
- Use a shared `cn`/merge helper for conditional utility classes.
- Do not fork a library primitive merely to change padding or color; use tokens,
  variants, or a small composition.

## Provider contract

Shared components may require root context for tooltip, dialog, toast, theme, or
router behavior. Mount each provider once at the application boundary.

Where the library ships an all-in-one provider root, it is the convenient
default for a new host. A mature product MAY compose the individual providers
instead when it already owns error boundaries or needs a specific ordering. The
result MUST still provide exactly one functional surface for each global
service; two nested toast or dialog roots produce a surface that answers half
the calls.

## Icons

- Use one icon family per product unless brand assets require another source.
- Give icons a consistent optical size and stroke weight.
- An icon-only action MUST have an accessible name and normally a tooltip.
- Do not use an unfamiliar icon where a short label is clearer.
- Health, warning, and selection icons MUST follow the semantic status model.
- Do not hand-author SVG paths for generic actions already in the icon library.

## Tables, lists, and charts

- Use a simple semantic list for small, non-tabular content.
- Use a table when users compare values across columns.
- Adopt `DataTable`/`DataGrid` when sorting, filtering, selection, virtualization,
  or column behavior becomes product functionality.
- Charts MUST answer a question that the neighboring number cannot answer.
- Provide textual values and accessible summaries for visualizations.
- Lazy-load heavy viewers and editors outside the initial route when practical.

## Avoid component theatre

Do not add:

- a Card around every heading and value;
- a Badge for static metadata that plain text expresses better;
- a tooltip that contains essential instructions;
- a chart with too little data or no decision attached;
- a custom toast, clipboard hook, modal, or focus trap when the system owns one;
- a shared abstraction whose only consumer is the code being extracted.

## Reuse review

- Did we search the real library source and exports?
- Are we reusing behavior rather than copying appearance?
- Is the new component at the correct primitive/pattern/feature level?
- Are provider, theme, and router assumptions explicit?
- Does a heavy tool load only where needed?
