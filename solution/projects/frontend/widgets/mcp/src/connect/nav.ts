/**
 * Where the visitor is inside the widget: a small state machine, no router. Pure, so the back rules are tested without a DOM.
 *
 * home -> brand (an app tile, with all its ways to connect) | manual. Back always returns home.
 */

export type View = { kind: 'home' } | { kind: 'brand'; id: string } | { kind: 'manual' };

export const HOME: View = { kind: 'home' };

export function backOf(_view: View): View {
  return HOME;
}

/** The crumbs from the root to the current screen; the last is the screen itself. */
export type Crumb = { kind: 'root' } | { kind: 'brand'; id: string } | { kind: 'manual' };

export function trail(view: View): Crumb[] {
  switch (view.kind) {
    case 'home':
      return [{ kind: 'root' }];
    case 'manual':
      return [{ kind: 'root' }, { kind: 'manual' }];
    case 'brand':
      return [{ kind: 'root' }, { kind: 'brand', id: view.id }];
  }
}
