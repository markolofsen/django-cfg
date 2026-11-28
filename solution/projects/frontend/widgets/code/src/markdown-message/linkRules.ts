import React from 'react';
import type { ComponentProps, ComponentType } from 'react';
import type { Components } from 'react-markdown';
import type { LinkRule } from './types';

// react-markdown's `Components['a']` is `keyof IntrinsicElements | ComponentType<…>`,
// so it isn't necessarily a function we can directly call. This is the
// component-shaped variant — what callers practically pass when they
// override `a`.
type AComponent = ComponentType<ComponentProps<'a'>>;

/** Run every rule's `preprocess` hook in order. Errors in a single
 *  rule are logged and skipped — the other rules still run. */
export function applyPreprocess(
  source: string,
  rules: readonly LinkRule[] | undefined,
): string {
  if (!rules || rules.length === 0) return source;
  let s = source;
  for (const rule of rules) {
    if (!rule.preprocess) continue;
    try {
      s = rule.preprocess(s);
    } catch (err) {
      console.warn(
        `[MarkdownMessage] linkRule "${rule.name ?? '(anonymous)'}" preprocess threw; skipping`,
        err,
      );
    }
  }
  return s;
}

/** Union of `extraHrefProtocols` and any `protocols` declared by rules. */
export function collectProtocols(
  extraHrefProtocols: readonly string[] | undefined,
  rules: readonly LinkRule[] | undefined,
): readonly string[] | undefined {
  const set = new Set<string>();
  if (extraHrefProtocols) for (const p of extraHrefProtocols) set.add(p);
  if (rules) {
    for (const r of rules) {
      if (r.protocols) for (const p of r.protocols) set.add(p);
    }
  }
  return set.size === 0 ? undefined : Array.from(set);
}

/** Build a custom `a` renderer that dispatches to the first matching
 *  rule, falling through to `callerA` (or the built-in chat anchor)
 *  for anything no rule claims. */
export function buildLinkRulesComponent(
  rules: readonly LinkRule[],
  isUser: boolean,
  callerA: NonNullable<Components['a']> | undefined,
): NonNullable<Components['a']> {
  const Renderer: AComponent = (props) => {
    const { href, children } = props;
    if (typeof href === 'string') {
      for (const rule of rules) {
        if (rule.match(href)) {
          return React.createElement(
            React.Fragment,
            null,
            rule.render({ href, children, isUser }),
          );
        }
      }
    }
    // Defer to the caller's `a` override if any. We only call it when
    // it's a function/component — string-form intrinsic overrides
    // (`'a' | 'span' | …`) aren't a thing react-markdown supports for
    // tag overrides, but the type still admits the union, so guard.
    if (callerA && typeof callerA === 'function') {
      const Caller = callerA as AComponent;
      return React.createElement(Caller, props);
    }
    // Fall through to the built-in anchor by rendering a plain `<a>`.
    return React.createElement('a', props, children);
  };
  return Renderer as NonNullable<Components['a']>;
}
