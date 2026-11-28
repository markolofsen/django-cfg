'use client';

import { useTreeContext } from '../context/TreeContext';

export interface TreeIndentGuidesProps {
  level: number;
  indent: number;
}

/**
 * Vertical guide lines under nested rows. Renders one absolute-positioned
 * 1px column per ancestor level. Decorative — `aria-hidden` and
 * pointer-events disabled. Opacity comes from the tree appearance.
 */
export function TreeIndentGuides({ level, indent }: TreeIndentGuidesProps) {
  const { appearance } = useTreeContext();
  if (level <= 0) return null;
  return (
    <span
      aria-hidden
      className="pointer-events-none absolute inset-y-0 left-0"
      style={{ width: 8 + level * indent, opacity: appearance.indentGuideOpacity }}
    >
      {Array.from({ length: level }).map((_, i) => (
        <span
          key={i}
          className="absolute inset-y-0 w-px bg-border"
          style={{ left: 8 + i * indent + indent / 2 - 0.5 }}
        />
      ))}
    </span>
  );
}
