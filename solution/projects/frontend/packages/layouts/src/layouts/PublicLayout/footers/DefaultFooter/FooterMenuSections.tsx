'use client';

import React from 'react';

import { Link } from '@djangocfg/ui-core/components';

import { FOOTER_LINK_TOUCH } from './touch';
import type { FooterMenuSection } from './types';

export interface FooterMenuSectionsProps {
  menuSections: FooterMenuSection[];
  minColumnWidth?: number;
  maxColumns?: number;
}

export function FooterMenuSections({
  menuSections,
  minColumnWidth = 180,
  maxColumns = 5,
}: FooterMenuSectionsProps) {
  if (menuSections.length === 0) return null;

  const effectiveColumns = Math.max(1, Math.min(maxColumns, menuSections.length));

  return (
    <div
      className="w-full grid gap-8 lg:gap-x-12"
      style={{ gridTemplateColumns: `repeat(${effectiveColumns}, minmax(${minColumnWidth}px, 1fr))` }}
    >
      {menuSections.map((section) => (
        <div key={section.title} className="min-w-0">
          <h3 className="text-xs font-medium text-muted-foreground mb-3">
            {section.title}
          </h3>
          <ul className="space-y-2 pointer-coarse:space-y-0">
            {section.items.map((item) => (
              <li key={item.path}>
                <Link
                  href={item.path}
                  className={`text-sm text-foreground/90 hover:text-foreground transition-colors ${FOOTER_LINK_TOUCH}`}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
