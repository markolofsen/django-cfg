'use client';

import React from 'react';

import { Link } from '@djangocfg/ui-core/components';
import { DjangoCFGLogo } from './DjangoCFGLogo';

import { FOOTER_LINK_TOUCH } from './touch';
import type { FooterLink } from './types';

export interface FooterBottomProps {
  copyright: string;
  credits?: {
    text: string;
    url?: string;
  };
  links?: FooterLink[];
  variant?: 'mobile' | 'desktop';
}

export function FooterBottom({
  copyright,
  credits,
  links = [],
  variant = 'desktop',
}: FooterBottomProps) {
  const isMobile = variant === 'mobile';

  if (isMobile) {
    return (
      <div className="border-t border-border pt-4">
        <div className="text-center space-y-2">
          <div className="text-xs text-muted-foreground">{copyright}</div>
          {credits && (
            <div className="text-xs text-muted-foreground flex items-center justify-center gap-1.5">
              {credits.url ? (
                <a
                  href={credits.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors flex items-center gap-1.5"
                >
                  <DjangoCFGLogo size={12} className="text-foreground" />
                  {credits.text}
                </a>
              ) : (
                <>
                  <DjangoCFGLogo size={12} className="text-foreground" />
                  {credits.text}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="border-t border-border mt-8 pt-6">
      <div className="flex flex-col md:flex-row justify-between items-center space-y-3 md:space-y-0 gap-4">
        <div className="text-xs text-muted-foreground">{copyright}</div>

        {credits && (
          <div className="text-xs text-muted-foreground flex items-center gap-1.5">
            {credits.url ? (
              <a
                href={credits.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors flex items-center gap-1.5"
              >
                <DjangoCFGLogo size={14} className="text-foreground" />
                {credits.text}
              </a>
            ) : (
              <>
                <DjangoCFGLogo size={14} className="text-foreground" />
                {credits.text}
              </>
            )}
          </div>
        )}

        {links.length > 0 && (
          <div className="flex flex-wrap items-center gap-3 md:gap-4 justify-center md:justify-end">
            {links.map((link) =>
              link.external ? (
                <a
                  key={link.path}
                  href={link.path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`text-xs text-muted-foreground hover:text-primary transition-colors ${FOOTER_LINK_TOUCH}`}
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  key={link.path}
                  href={link.path}
                  className={`text-xs text-muted-foreground hover:text-primary transition-colors ${FOOTER_LINK_TOUCH}`}
                >
                  {link.label}
                </Link>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}
