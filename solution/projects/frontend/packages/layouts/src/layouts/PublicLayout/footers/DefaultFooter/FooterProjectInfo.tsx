'use client';

import React from 'react';

import { FooterSocialLinksComponent } from './FooterSocialLinks';

import type { LucideIcon } from 'lucide-react';
import type { FooterSocialLinks } from './types';

export interface FooterProjectInfoProps {
  /** Brand row: custom node, or a plain string (styled title). */
  brand?: React.ReactNode;
  description?: string;
  badge?: {
    icon: LucideIcon;
    text: string;
  };
  socialLinks?: FooterSocialLinks;
  variant?: 'mobile' | 'desktop';
}

export function FooterProjectInfo({
  brand,
  description,
  badge,
  socialLinks,
  variant = 'desktop',
}: FooterProjectInfoProps) {
  const isMobile = variant === 'mobile';

  const showBrand = brand != null && brand !== '' && brand !== false;

  return (
    <div className={isMobile ? 'text-center space-y-4 mb-6' : 'space-y-4 lg:flex-shrink-0 lg:w-80'}>
      {showBrand && (
        <div className={isMobile ? 'flex items-center justify-center gap-2' : 'flex items-center gap-2'}>
          {typeof brand === 'string' ? (
            <span className={isMobile ? 'text-lg font-bold text-foreground' : 'text-lg font-semibold text-foreground'}>
              {brand}
            </span>
          ) : (
            brand
          )}
        </div>
      )}

      {description && (
        <p className={isMobile ? 'text-muted-foreground text-sm leading-relaxed max-w-md mx-auto' : 'text-muted-foreground text-xs leading-relaxed max-w-xs'}>
          {description}
        </p>
      )}

      {badge && !isMobile && (
        <div className="pt-2">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/25 bg-primary/15 px-3 py-1 text-xs font-semibold text-primary">
            <badge.icon className="w-4 h-4" />
            {badge.text}
          </span>
        </div>
      )}

      {socialLinks && (
        <FooterSocialLinksComponent
          socialLinks={socialLinks}
          className={isMobile ? 'flex justify-center space-x-6' : 'flex space-x-4 pt-4'}
        />
      )}
    </div>
  );
}
