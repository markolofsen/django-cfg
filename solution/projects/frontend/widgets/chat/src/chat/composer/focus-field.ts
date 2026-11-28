/**
 * Put the caret back in the composer's field, at the END of the draft.
 *
 * Two controls need this and neither owns the textarea: the form's padding
 * (a press on empty space means "keep typing") and the tool menu (a pick is a
 * statement of intent, and the sentence naming its object comes next). The
 * field's own ref is deliberately local to `ComposerField`, so the shared route
 * is the DOM — both callers render inside the same `<form>`.
 *
 * Kept in one place because the "caret at the end" half is the part that goes
 * wrong: `focus()` alone leaves it wherever the browser last had it, which on a
 * written draft is the beginning.
 */

/**
 * Focus the composer's textarea within `root`, caret after the last character.
 *
 * A no-op when the field already holds focus — re-running the selection would
 * fight a caret the user just placed by clicking.
 */
export function focusComposerField(root: HTMLElement | null | undefined): void {
  const field = root?.querySelector("textarea");
  if (!field || field === document.activeElement) return;
  // `preventScroll`: the browser's own scroll-into-view moves ancestors and the page; the transcript pins itself.
  field.focus({ preventScroll: true });
  const end = field.value.length;
  field.setSelectionRange(end, end);
}
