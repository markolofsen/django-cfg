---
title: Navigation, Layout, and Responsive Behavior
status: current
version: "3.0"
audience: product, design, frontend, agents
last_reviewed: 2026-09-01
---

# Navigation, Layout, and Responsive Behavior

Navigation is product state. Layout must preserve the user's task across route,
viewport, input mode, and refresh.

## URL as durable state

Use a stable URL when a state should survive reload, browser history, a shared
link, or direct entry.

Good URL state:

- selected entity or detail route;
- major section or tab with independent content;
- search/filter/sort that changes the result set;
- active conversation or work session;
- pagination cursor when shareability matters.

Keep hover, temporary disclosure, draft input, and one-off animation state out of
the URL.

## One route registry

A product SHOULD define route identity, path roots, shell metadata, navigation
labels, and active-state relationships in one declarative registry. Typed path
builders consume it.

- Never concatenate internal URLs across features.
- Encode dynamic segments and query values.
- Centralize query-key names.
- Preserve intentional aliases and canonicalize old forms.
- A feature emits navigation intent; the shell applies product routing.
- Use real links for destinations so open-in-new-tab and accessibility work.

## Navigation hierarchy

Use the smallest hierarchy that matches the product:

1. Global rail or top navigation for durable product areas.
2. Area-level master navigation for a family of related destinations.
3. Tabs for sibling views of the same object or task.
4. Disclosure for optional detail inside one view.

Do not use tabs as a substitute for routes when users need history or deep links.
Do not put rare diagnostics into global navigation merely because space exists.

## Selection and status

Selection MUST remain visually distinct from health or attention.

- Active navigation uses shape, surface, and `aria-current`.
- Health uses a small semantic indicator with an accessible label.
- Unread/attention uses a count or dot only when it represents real unseen
  content.
- Never add decorative dots to every item.
- Tooltips may add detail but do not replace the accessible name.

## Master/detail

Master/detail works well for settings, resources, and operational consoles when
users repeatedly move between peers.

Desktop:

- keep master navigation stable;
- let detail own its scroll region;
- use one clear detail heading;
- maintain a consistent content width by content type.

Compact viewport:

- show master and detail as separate views;
- direct links MAY open detail immediately;
- provide a clear Back action;
- restore focus to the selected master item;
- preserve browser history when selection is URL-backed.

Sharing layout mechanics does not mean sharing domain content policy.

## Layout primitives

- Use a persistent shell for global navigation and status when route changes
  should not remount them.
- Define recurring reading, wide, and breakout widths as layout tokens.
- Prefer CSS Grid for multi-axis page structure and flex for one-dimensional
  alignment.
- Every scroll region needs an explicit owner. Avoid nested scrolling unless the
  inner region is a real tool such as a terminal or log viewer.
- Reserve space for lazy content to prevent layout shift.
- Use `min-height: 100dvh` semantics for viewport layouts; account for browser
  chrome and safe areas.

## Responsive design is task adaptation

For each multi-column region, specify behavior below the breakpoint:

- what remains visible;
- what becomes a separate step or route;
- what changes order;
- what can scroll horizontally;
- where actions move;
- how focus and context are preserved.

Do not rely on "everything stacks". A dense table may need column priority,
row detail, or horizontal scroll. A toolbar may need a menu. A master/detail
view needs two compact states.

## Breakpoints and input modes

- Choose breakpoints where the content stops working, not by named devices.
- Test narrow touch, wide touch, keyboard/mouse, and zoomed desktop.
- Hover cannot be the only way to discover or perform an action.
- Touch targets SHOULD be at least 44 by 44 CSS pixels where space allows;
  compact desktop controls MAY be smaller with sufficient spacing and keyboard
  access.
- Do not infer touch capability from viewport width alone.

## Scroll and focus continuity

- Route changes normally reset the detail scroll, not persistent shell scroll.
- Back navigation SHOULD restore prior selection and useful scroll position.
- Opening and closing compact detail restores focus.
- Lazy-route fallbacks replace only the changing content region.
- Background refresh MUST not steal focus or scroll.

## Navigation review

- Can every durable destination be bookmarked and reopened?
- Is URL construction centralized and typed?
- Are active, healthy, and unread visually and semantically separate?
- Does compact layout preserve the workflow and focus path?
- Is there exactly one intentional scroll owner per region?
- Does the shell remain stable while feature chunks and data load?

