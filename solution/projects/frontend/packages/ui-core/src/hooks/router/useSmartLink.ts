'use client';

/**
 * useSmartLink — turn a non-`<a>` element (card, table row, list item)
 * into a proper link.
 *
 * WHY:
 *   "Clickable cards" used to either nest an `<a>` (which then can't
 *   contain other interactive children) or attach `onClick={navigate}`
 *   (which loses cmd-click, middle-click, keyboard, accessibility).
 *   This hook returns a small bag of handlers that gives a non-anchor
 *   element the right behavior in all those cases.
 *
 *   Key behaviors:
 *     - Cmd/Ctrl+click and middle-click open in a new tab.
 *     - Plain click does SPA nav.
 *     - Enter / Space activate from keyboard.
 *     - Clicks inside nested `<a>` / `<button>` are ignored (so the
 *       inner element handles its own action).
 *     - `role="link"` and `tabIndex={0}` for screen readers / keyboard.
 *
 * @example
 *   const link = useSmartLink('/products/42');
 *   <div {...link}>Product card</div>
 */

import { useCallback, useMemo, type KeyboardEvent, type MouseEvent } from 'react';
import { useNavigate, type NavigateOptions } from './useNavigate';

export interface UseSmartLinkOptions extends NavigateOptions {
  /** Disable all navigation (e.g. while a row is being edited). */
  disabled?: boolean;
  /**
   * If true, modifier-clicks (cmd/ctrl) and middle-clicks DON'T open
   * a new tab — they're treated as plain clicks. Default: false.
   */
  ignoreModifiers?: boolean;
}

export interface SmartLinkHandlers {
  onClick: (event: MouseEvent<HTMLElement>) => void;
  onAuxClick: (event: MouseEvent<HTMLElement>) => void;
  onKeyDown: (event: KeyboardEvent<HTMLElement>) => void;
  role: 'link';
  /** -1 when disabled so the element is removed from the tab order. */
  tabIndex: 0 | -1;
  /** Forwarded to the consumer element so AT announces disabled state. */
  'aria-disabled'?: true;
}

const INTERACTIVE_SELECTOR =
  'a,button,input,textarea,select,label,[role="button"],[role="link"],[role="checkbox"],[role="switch"],[role="tab"],[role="menuitem"]';

/**
 * True if the click target is inside another interactive element
 * nested within `currentTarget` — in which case we shouldn't intercept.
 * Uses Element.closest for a single C-side traversal that also handles
 * SVG/MathML, custom elements, and `:where()` semantics correctly.
 */
function isInsideNestedInteractive(event: MouseEvent<HTMLElement>): boolean {
  const target = event.target as Element | null;
  const current = event.currentTarget;
  if (!target || target === current) return false;
  const interactive = target.closest(INTERACTIVE_SELECTOR);
  // Found an interactive ancestor strictly between target and currentTarget.
  return !!interactive && interactive !== current && current.contains(interactive);
}

/** True if the user has selected text — don't navigate, they're reading. */
function hasTextSelection(): boolean {
  if (typeof window === 'undefined') return false;
  const selection = window.getSelection();
  return !!selection && selection.toString().length > 0;
}

/**
 * Hook variant — gives an element link semantics with keyboard + new-tab support.
 */
export function useSmartLink(
  href: string,
  options?: UseSmartLinkOptions
): SmartLinkHandlers {
  const { navigate } = useNavigate();
  const disabled = options?.disabled ?? false;
  const ignoreModifiers = options?.ignoreModifiers ?? false;
  const replace = options?.replace;
  const scroll = options?.scroll;

  const openInNewTab = useCallback((url: string) => {
    if (typeof window === 'undefined') return;
    window.open(url, '_blank', 'noopener,noreferrer');
  }, []);

  const onClick = useCallback(
    (event: MouseEvent<HTMLElement>) => {
      if (disabled) return;
      if (event.defaultPrevented) return;
      if (isInsideNestedInteractive(event)) return;
      if (hasTextSelection()) return;

      // Modifier click → open in new tab. Don't preventDefault on a
      // real <a>, but for div/span our default IS to navigate so we
      // can branch freely.
      if (
        !ignoreModifiers &&
        (event.metaKey || event.ctrlKey || event.shiftKey)
      ) {
        event.preventDefault();
        openInNewTab(href);
        return;
      }

      event.preventDefault();
      navigate(href, { replace, scroll });
    },
    [disabled, ignoreModifiers, navigate, href, replace, scroll, openInNewTab]
  );

  const onAuxClick = useCallback(
    (event: MouseEvent<HTMLElement>) => {
      if (disabled) return;
      if (event.defaultPrevented) return;
      if (isInsideNestedInteractive(event)) return;
      // Middle-click only.
      if (event.button !== 1) return;
      if (ignoreModifiers) return;
      event.preventDefault();
      openInNewTab(href);
    },
    [disabled, ignoreModifiers, href, openInNewTab]
  );

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLElement>) => {
      if (disabled) return;
      // Only handle when the focused element IS the link container,
      // otherwise we steal Enter from inputs etc.
      if (event.target !== event.currentTarget) return;
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      navigate(href, { replace, scroll });
    },
    [disabled, navigate, href, replace, scroll]
  );

  return useMemo<SmartLinkHandlers>(
    () => ({
      onClick,
      onAuxClick,
      onKeyDown,
      role: 'link',
      tabIndex: disabled ? -1 : 0,
      ...(disabled ? { 'aria-disabled': true as const } : {}),
    }),
    [onClick, onAuxClick, onKeyDown, disabled]
  );
}
