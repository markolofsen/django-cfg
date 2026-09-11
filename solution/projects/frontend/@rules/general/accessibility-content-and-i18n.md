---
title: Accessibility, Content, and Internationalization
status: current
version: "3.0"
audience: product, design, frontend, qa, agents
last_reviewed: 2026-09-01
---

# Accessibility, Content, and Internationalization

Accessibility and language are product architecture. They cannot be repaired by
adding labels after the interaction model is complete.

## Baseline

Interactive product UI MUST:

- use semantic HTML before ARIA;
- support keyboard operation and visible focus;
- maintain WCAG AA contrast for text and controls;
- work at 200% zoom without loss of task or content;
- expose names, roles, states, and errors to assistive technology;
- respect reduced motion and system color preferences;
- avoid color, sound, or motion as the only signal.

Target size, contrast, and focus appearance SHOULD follow WCAG 2.2 guidance.
Use automated checks as a floor, not proof of usability.

## Semantic interaction

- Use `button` for actions and `a` for navigation.
- Headings describe a logical outline; do not choose levels for font size.
- Lists, tables, forms, and landmarks use their native elements.
- A clickable row must still expose its primary destination and nested actions
  without invalid nested controls.
- Disabled controls SHOULD be avoided when an explanation and available path is
  more useful. If disabled, the reason must be discoverable.

## Accessible names

- Visible text is the preferred name.
- Icon-only controls require `aria-label` or an associated visible label.
- Decorative icons use `aria-hidden`.
- Status labels include the object when context is otherwise ambiguous.
- Tooltips supplement names; they do not provide the only name.
- Do not repeat the same content through both visible text and an extra ARIA
  label that causes duplicate announcements.

## Focus management

- Opening a modal moves focus into it; closing returns focus to the initiator.
- Compact master/detail navigation restores focus to the selected row on Back.
- Route changes move focus to the new main heading or content boundary when
  needed, without surprising pointer users.
- Async refresh does not steal focus.
- New errors are associated with the relevant field and announced when needed.
- Focus must never be trapped outside a real modal interaction.

## Product copy

Copy should reduce uncertainty.

- Use concrete verbs: "Copy address", "Stop engine", "Retry connection".
- Name the object in destructive and ambiguous actions.
- State what happened, its impact, and the recovery action.
- Prefer user/domain language over protocol or implementation terms.
- Avoid blame, jokes in failure states, false reassurance, and ornamental prose.
- Keep labels stable across navigation, command palette, shortcuts, and docs.
- Use sentence case unless a platform convention requires otherwise.

Status copy SHOULD combine meaning and state:

```text
Online and ready
Reconnecting to the server
Server stopped
Status unavailable
```

Raw codes belong in technical detail or logs.

## Errors

An actionable error answers:

1. What failed?
2. What remains available?
3. What can the user do now?
4. Where can an expert inspect detail?

Do not expose raw exceptions, stack traces, request IDs, or backend prose as the
primary message. A request ID MAY appear in expandable diagnostic detail.

## Internationalization ownership

- Visible product text belongs in a feature-owned namespace.
- Keep the common namespace small: only truly shared actions and phrases.
- Bind the namespace once in the feature; do not repeat it in every key.
- The source locale defines the typed schema.
- Validate missing keys, extra keys, value shape, and interpolation variables.
- Fallback is a runtime safety net, not permission to accumulate locale drift.
- Dates, numbers, relative time, lists, and plurals use locale-aware formatters
  from the shared utilities, never hand-rolled at the call site.
- Do not build sentences by concatenating translated fragments.
- **CLI commands, flags, package names, slash commands, config keys, and code
  examples stay byte-for-byte identical in every locale.** Translate the
  sentence around them. A translated flag is a command that fails for the reader
  who copies it, and the failure names nothing about the translation.

## Layout for language variance

- Expect labels to grow by 30-50%.
- Buttons remain one readable line for common actions; shorten copy before
  shrinking text.
- Avoid fixed widths around translated text.
- Test long strings, plural extremes, and empty values.
- Set `<html lang>` and direction from the resolved locale.
- Use logical CSS properties so RTL does not require a parallel layout.
- Icons that imply direction must mirror when meaning changes in RTL; universal
  media controls usually do not.

## Time, units, and identifiers

- Show absolute time when auditability matters and relative time when recency is
  the decision. Provide both when useful.
- State time zone for scheduled or cross-region operations.
- **Display time has ONE owner: the shared format utilities.** A screen imports
  a formatter; it does not reach for `Intl.DateTimeFormat`, `toLocaleTimeString`
  or `Date` arithmetic itself. Three surfaces spelled the same clock three ways
  — an `Intl` formatter with one options object, `toLocaleTimeString` with
  another, and a feature-local helper — so one instant rendered differently on
  adjacent rows and nothing looked broken until they were compared.
- **Never derive a comparison from a formatted string.** Grouping rows by day
  through their rendered label merges the same date in different years, because
  a short date format omits the year. Compare the value; format for the reader.
- A format is not copy. Formats live in the utilities and follow the reader's
  locale; the i18n catalogue carries WORDS. A hand-written `HH:mm` imposes a
  24-hour clock on locales that use a 12-hour one, and a per-language date
  pattern in a catalogue is a second, worse formatter.
- Do not localize opaque IDs, command text, paths, or machine-readable values.
- Use monospace selectively for commands, identifiers, logs, and aligned numeric
  data, not for all technical-looking copy.

## Sound and notifications

- Sound is supplementary and user-controllable.
- Desktop/browser notifications require permission and a clear product benefit.
- Do not repeatedly prompt after denial.
- A notification links to a stable destination when action is possible.
- Critical state remains visible in the product after a transient notification
  disappears.

## Review

- Can the full workflow be completed with keyboard only?
- Are focus, zoom, contrast, and reduced motion verified?
- Does every icon-only action have a useful name?
- Are errors actionable and free of raw implementation detail?
- Do long translations and RTL preserve task order?
- Are time, units, and status understandable without color or sound?

