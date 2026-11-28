/**
 * LucideIcon Component
 *
 * Smart component for rendering Lucide icons
 * Supports both string names and icon components
 *
 * Usage:
 * ```tsx
 * // By name (string) — PascalCase or kebab-case
 * <LucideIcon icon="CloudLightning" className="w-4 h-4" />
 *
 * // By component
 * import { CloudLightning } from 'lucide-react';
 * <LucideIcon icon={CloudLightning} className="w-4 h-4" />
 * ```
 *
 * A name loads that one icon on demand. `import * as` from lucide-react put
 * all ~1,600 icons (~180 KB gz) into every app that reached this barrel.
 */

'use client';

import { CloudLightning } from 'lucide-react';
import { DynamicIcon, iconNames } from 'lucide-react/dynamic';
import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { IconName } from 'lucide-react/dynamic';
import type { LucideIcon as LucideIconType } from 'lucide-react';
export interface LucideIconProps extends Omit<React.SVGProps<SVGSVGElement>, 'children'> {
  /**
   * Icon name (string) or icon component (LucideIcon)
   * If string, will be resolved from lucide-react
   * If component, will be used directly
   */
  icon?: LucideIconType | string;
  /**
   * Fallback icon if name not found
   * @default CloudLightning
   */
  fallback?: LucideIconType;
  /**
   * Additional CSS classes
   */
  className?: string;
}

// "ArrowUp01" and "arrow-up-0-1" both fold to "arrowup01".
let byFolded: Map<string, IconName> | undefined;

function resolveIconName(name: string): IconName | undefined {
  byFolded ??= new Map(iconNames.map((n) => [n.replace(/-/g, ''), n as IconName]));
  return byFolded.get(name.replace(/[-_\s]/g, '').toLowerCase());
}

/**
 * LucideIcon Component
 *
 * Renders a Lucide icon either by name (string) or by component reference.
 * A name renders an empty box of the same size until its icon loads.
 */
export function LucideIcon({
  icon,
  fallback = CloudLightning,
  className,
  ...props
}: LucideIconProps) {
  if (typeof icon === 'string') {
    const name = resolveIconName(icon);
    if (name) {
      const Placeholder = () => <span aria-hidden className={cn('inline-block', className)} />;
      return (
        <DynamicIcon
          {...(props as Omit<React.SVGProps<SVGSVGElement>, 'ref' | 'name'>)}
          name={name}
          className={cn(className)}
          fallback={Placeholder}
        />
      );
    }
  }

  const IconComponent = icon && typeof icon !== 'string' ? icon : fallback;
  return <IconComponent className={cn(className)} {...props} />;
}
