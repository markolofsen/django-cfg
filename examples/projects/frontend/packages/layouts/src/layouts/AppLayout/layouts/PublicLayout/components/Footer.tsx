/**
 * Footer Component
 *
 * Responsive footer with Desktop and Mobile variants
 * Refactored from _old/MainLayout - uses context only!
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { useIsMobile } from '@djangocfg/ui/hooks';
import { useAppContext } from '../../../context';

/**
 * Footer Component
 *
 * Features:
 * - Responsive (Desktop/Mobile variants)
 * - Project info with logo and description
 * - Badge (optional)
 * - Social links (GitHub, LinkedIn, Twitter, Telegram)
 * - Menu sections (single items or grouped)
 * - Legal links (Privacy, Terms, Security, Cookies, etc.)
 * - Copyright and branding
 *
 * All data from context!
 */
export function Footer() {
  const { config } = useAppContext();
  const isMobile = useIsMobile();

  const { app, publicLayout } = config;
  const footer = publicLayout.footer;
  const currentYear = new Date().getFullYear();

  if (isMobile) {
    return (
      <footer className="lg:hidden bg-background border-t border-border mt-auto">
        <div className="w-full px-4 py-8">
          {/* Project Info */}
          <div className="text-center space-y-4 mb-6">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-6 h-6 flex items-center justify-center">
                <img
                  src={app.logoPath}
                  alt={`${app.name} Logo`}
                  className="w-full h-full object-contain"
                />
              </div>
              <span className="text-lg font-bold text-foreground">{app.name}</span>
            </div>
            {app.description && (
              <p className="text-muted-foreground text-sm leading-relaxed max-w-md mx-auto">
                {app.description}
              </p>
            )}
          </div>

          {/* Quick Links */}
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            {footer.links.docs && (
              <a
                href={footer.links.docs}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
                title="Documentation"
              >
                Docs
              </a>
            )}
            {footer.links.privacy && (
              <Link
                href={footer.links.privacy}
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Privacy
              </Link>
            )}
            {footer.links.terms && (
              <Link
                href={footer.links.terms}
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Terms
              </Link>
            )}
          </div>

          {/* Bottom Section */}
          <div className="border-t border-border pt-4">
            <div className="text-center space-y-2">
              <div className="text-sm text-muted-foreground">
                © {currentYear} {app.name}. All rights reserved.
              </div>
              <div className="text-sm text-muted-foreground">
                Made with ❤️ by{' '}
                <a
                  href="https://reforms.ai"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  ReformsAI
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    );
  }

  // Desktop Footer
  return (
    <footer className="max-lg:hidden bg-background border-t border-border mt-auto">
      <div className="w-full px-8 lg:px-16 xl:px-24 py-12">
        <div className="flex flex-col gap-8">
          {/* Top Section - Two Column Layout */}
          <div className="flex gap-8">
            {/* Left Column - Project Info */}
            <div className="space-y-4" style={{ width: '30%', minWidth: '300px' }}>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 flex items-center justify-center">
                  <img
                    src={app.logoPath}
                    alt={`${app.name} Logo`}
                    className="w-full h-full object-contain"
                  />
                </div>
                <span className="text-xl font-bold text-foreground">{app.name}</span>
              </div>
              {app.description && (
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {app.description}
                </p>
              )}
              {/* Badge */}
              {footer.badge && (
                <div className="pt-2">
                  <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-sm bg-primary/10 hover:bg-primary/15 border border-primary/20 text-xs font-medium text-primary transition-colors">
                    <footer.badge.icon className="w-3.5 h-3.5" />
                    {footer.badge.text}
                  </span>
                </div>
              )}
            </div>

            {/* Right Column - Footer Menu Sections */}
            <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 flex-1">
              {footer.menuSections.map((section) => {
                // Single item section - render as direct link
                if (section.items.length === 1) {
                  const item = section.items[0];
                  if (!item) return null;

                  return (
                    <div key={section.title}>
                      <Link
                        href={item.path}
                        className="text-muted-foreground hover:text-primary text-sm transition-colors"
                      >
                        {item.label}
                      </Link>
                    </div>
                  );
                }

                // Multiple items - render as section
                return (
                  <div key={section.title}>
                    <h3 className="text-lg font-semibold text-foreground mb-4">
                      {section.title}
                    </h3>
                    <ul className="space-y-2">
                      {section.items.map((item) => (
                        <li key={item.path}>
                          <Link
                            href={item.path}
                            className="text-muted-foreground hover:text-primary text-sm transition-colors"
                          >
                            {item.label}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Bottom Section */}
          <div className="border-t border-border" style={{ marginTop: '2rem', paddingTop: '2rem' }}>
            <div className="flex justify-between items-center gap-4">
            <div className="text-xs text-muted-foreground">
              © {currentYear} {app.name}. All rights reserved.
            </div>
            <div className="text-xs text-muted-foreground flex items-center gap-1">
              Made with ❤️ by{' '}
              <a
                href="https://reforms.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                ReformsAI
              </a>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              {footer.links.docs && (
                <a
                  href={footer.links.docs}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-muted-foreground hover:text-primary transition-colors"
                  title="Documentation"
                >
                  Docs
                </a>
              )}
              {footer.links.privacy && (
                <Link
                  href={footer.links.privacy}
                  className="text-xs text-muted-foreground hover:text-primary transition-colors"
                >
                  Privacy Policy
                </Link>
              )}
              {footer.links.terms && (
                <Link
                  href={footer.links.terms}
                  className="text-xs text-muted-foreground hover:text-primary transition-colors"
                >
                  Terms of Service
                </Link>
              )}
              {footer.links.security && (
                <Link
                  href={footer.links.security}
                  className="text-xs text-muted-foreground hover:text-primary transition-colors"
                >
                  Security
                </Link>
              )}
              {footer.links.cookies && (
                <Link
                  href={footer.links.cookies}
                  className="text-xs text-muted-foreground hover:text-primary transition-colors"
                >
                  Cookies
                </Link>
              )}
            </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
