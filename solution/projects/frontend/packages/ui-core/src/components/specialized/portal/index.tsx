'use client';

import * as React from 'react';
import { createPortal } from 'react-dom';

export interface PortalProps {
  children: React.ReactNode;
  /**
   * Target container. Defaults to document.body.
   * Accepts a DOM element, a function returning one, or a ref.
   */
  container?: Element | (() => Element | null) | React.RefObject<Element | null> | null;
  /** Render children in-place instead of teleporting. @default false */
  disablePortal?: boolean;
  /**
   * Keep children mounted in the DOM even when the portal is "closed"
   * (i.e. when the parent conditionally hides them via CSS / opacity).
   * Useful for exit animations — the node stays in the DOM while the
   * animation plays, then the parent unmounts it via its own state.
   * @default false
   */
  keepMounted?: boolean;
}

/**
 * Portal — renders children into a different part of the DOM tree,
 * escaping any CSS stacking context (transform, filter, will-change).
 *
 * @example
 * ```tsx
 * // Default: teleport to document.body
 * <Portal>
 *   <div className="fixed inset-0 z-50">Modal</div>
 * </Portal>
 *
 * // Custom container
 * <Portal container={() => document.getElementById('modal-root')}>
 *   <div>Content</div>
 * </Portal>
 *
 * // Keep mounted for exit animations — hide via CSS, unmount later
 * <Portal keepMounted>
 *   <div style={{ display: isOpen ? 'block' : 'none' }}>Animated panel</div>
 * </Portal>
 *
 * // Disable portal (render in-place, e.g. in tests or SSR)
 * <Portal disablePortal>
 *   <div>In-place</div>
 * </Portal>
 * ```
 */
export const Portal = React.forwardRef<HTMLDivElement, PortalProps>(
  function Portal(props, ref) {
    const { children, container, disablePortal = false, keepMounted = false } = props;
    const [mountNode, setMountNode] = React.useState<Element | null>(null);

    React.useEffect(() => {
      if (!disablePortal) {
        setMountNode(getContainer(container) || document.body);
      }
    }, [container, disablePortal]);

    if (disablePortal) {
      if (React.isValidElement(children)) {
        return React.cloneElement(children as React.ReactElement<{ ref?: React.Ref<HTMLDivElement> }>, { ref });
      }
      return <>{children}</>;
    }

    // SSR / before first effect: keepMounted renders in-place so content
    // exists in the server HTML; otherwise return null (portal attaches client-side).
    if (!mountNode) {
      return keepMounted ? <>{children}</> : null;
    }

    return createPortal(children, mountNode);
  }
);

Portal.displayName = 'Portal';

/**
 * Resolves the container from various input types
 */
function getContainer(
  container: PortalProps['container']
): Element | null {
  if (container === null || container === undefined) {
    return null;
  }

  if (typeof container === 'function') {
    return container();
  }

  if ('current' in container) {
    return container.current;
  }

  return container;
}

export type { PortalProps as PortalPropsType };
