'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ScrollSpyProvider, useScrollSpyContext } from '../context';
import type {
  ScrollSpyProps,
  ScrollSpyNavProps,
  ScrollSpyNavItemProps,
  ScrollSpySectionProps,
} from '../types';

export function ScrollSpy({
  children,
  offset = 0,
  rootMargin = '0px 0px -80% 0px',
  onActiveChange,
}: ScrollSpyProps) {
  const [activeId, setActiveId] = React.useState<string | null>(null);
  // Registration must be state, not a ref: a `ScrollSpySection` registers from
  // an effect, and a ref write renders nothing — `sections` would stay empty
  // until something else re-rendered the provider.
  const [sectionMap, setSectionMap] = React.useState<Map<string, string>>(
    () => new Map()
  );
  const observerRef = React.useRef<IntersectionObserver | null>(null);

  const registerSection = React.useCallback((id: string, label: string) => {
    setSectionMap((prev) => {
      if (prev.get(id) === label) return prev;
      const next = new Map(prev);
      next.set(id, label);
      return next;
    });
  }, []);

  const unregisterSection = React.useCallback((id: string) => {
    setSectionMap((prev) => {
      if (!prev.has(id)) return prev;
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const handleSetActiveId = React.useCallback(
    (id: string) => {
      setActiveId(id);
      onActiveChange?.(id);
    },
    [onActiveChange]
  );

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        const top = visible[0];
        if (top) {
          handleSetActiveId(top.target.id);
        }
      },
      {
        rootMargin,
        threshold: [0, 0.25, 0.5, 0.75, 1],
      }
    );
    observerRef.current = observer;

    // Observe every registered section element.
    for (const id of sectionMap.keys()) {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [rootMargin, handleSetActiveId, sectionMap]);

  const sections = React.useMemo(
    () =>
      Array.from(sectionMap.entries()).map(([id, label]) => ({
        id,
        label,
      })),
    [sectionMap]
  );

  const value = React.useMemo(
    () => ({
      activeId,
      sections,
      offset,
      registerSection,
      unregisterSection,
      setActiveId: handleSetActiveId,
    }),
    [
      activeId,
      sections,
      offset,
      registerSection,
      unregisterSection,
      handleSetActiveId,
    ]
  );

  return <ScrollSpyProvider value={value}>{children}</ScrollSpyProvider>;
}
ScrollSpy.displayName = 'ScrollSpy';

export function ScrollSpyNav({ children, className, ...props }: ScrollSpyNavProps) {
  return (
    <nav
      data-slot="scroll-spy-nav"
      className={cn('flex flex-col gap-1', className)}
      {...props}
    >
      {children}
    </nav>
  );
}
ScrollSpyNav.displayName = 'ScrollSpyNav';

export function ScrollSpyNavItem({
  sectionId,
  children,
  className,
  onClick,
  ...props
}: ScrollSpyNavItemProps) {
  const { activeId, offset } = useScrollSpyContext();
  const isActive = activeId === sectionId;

  const handleClick = React.useCallback(
    (e: React.MouseEvent<HTMLAnchorElement>) => {
      e.preventDefault();
      const el = document.getElementById(sectionId);
      if (el) {
        // `window.scrollTo`, not `scrollIntoView`: the latter has no way to
        // express `offset`, so a sticky header would cover the heading.
        const top =
          el.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
      onClick?.(e);
    },
    [sectionId, onClick, offset]
  );

  return (
    <a
      href={`#${sectionId}`}
      data-slot="scroll-spy-nav-item"
      data-active={isActive ? 'true' : undefined}
      onClick={handleClick}
      className={cn(
        'relative rounded-md px-3 py-1.5 text-sm transition-colors',
        'text-muted-foreground hover:text-foreground hover:bg-muted/50',
        isActive &&
          'font-medium text-foreground bg-muted before:absolute before:left-0 before:top-1.5 before:bottom-1.5 before:w-0.5 before:rounded-full before:bg-primary',
        className
      )}
      {...props}
    >
      {children}
    </a>
  );
}
ScrollSpyNavItem.displayName = 'ScrollSpyNavItem';

export function ScrollSpySection({
  id,
  label,
  children,
  className,
  ...props
}: ScrollSpySectionProps) {
  const { registerSection, unregisterSection } = useScrollSpyContext();

  React.useEffect(() => {
    registerSection(id, label);
    return () => unregisterSection(id);
  }, [id, label, registerSection, unregisterSection]);

  return (
    <div
      id={id}
      data-slot="scroll-spy-section"
      data-section-id={id}
      className={cn('scroll-mt-20', className)}
      {...props}
    >
      {children}
    </div>
  );
}
ScrollSpySection.displayName = 'ScrollSpySection';
