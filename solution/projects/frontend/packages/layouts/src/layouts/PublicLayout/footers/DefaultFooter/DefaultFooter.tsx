/**
 * Default Public Footer
 *
 * Professional, flexible footer with full / compact / simple variants.
 */

'use client';

import React, { memo } from 'react';

import { Link } from '@djangocfg/ui-core/components';

import { LocaleSwitcher } from '../../../_components/LocaleSwitcher';
import { useLayoutI18nOptional } from '../../../../shared/LayoutI18nProvider';
import { ThemeModeControl } from './ThemeModeControl';
import { FooterMenuSections } from './FooterMenuSections';
import { FooterProjectInfo } from './FooterProjectInfo';

import { FOOTER_LINK_TOUCH } from './touch';
import type { DefaultFooterProps } from './types';

function DefaultFooterRaw({ config }: DefaultFooterProps) {
  const variant = config.variant ?? 'full';
  const shellClass = config.shell?.className;
  const brandSlot = config.brand?.slot;
  const description = config.brand?.description;
  const badge = config.brand?.badge;
  const showBrandColumn = config.brand?.showColumn ?? true;
  const menuSections = config.menus?.sections ?? [];
  const menuColumnMinWidth = config.menus?.columnMinWidth ?? 180;
  const menuMaxColumns = config.menus?.maxColumns ?? 5;
  const links = config.links ?? [];
  const socialLinks = config.social;
  const copyrightProp = config.meta?.copyright;
  const creditsProp = config.meta?.credits;
  const i18n = useLayoutI18nOptional();
  const showThemeSwitcher = config.controls?.showThemeSwitcher !== false;
  const showLocaleSwitcher =
    config.controls?.showLocaleSwitcher !== false && Boolean(i18n);
  const showFooterControlsRow = showThemeSwitcher || showLocaleSwitcher;
  const slots = config.slots;

  const currentYear = new Date().getFullYear();
  const copyright = copyrightProp || `© ${currentYear}. All rights reserved.`;
  const credits = creditsProp;

  /**
   * Space below the footer's last row.
   *
   * The fallback is deliberately NOT `0px`: `env(safe-area-inset-bottom)`
   * resolves to zero on every device without a home indicator and in every
   * desktop browser, which left the final row (theme + locale controls on
   * mobile) flush against the viewport edge with nothing under it. `max()`
   * keeps a real gutter everywhere and still yields to a larger inset on
   * devices that report one.
   */
  const footerSafeBottom = 'pb-[max(1rem,env(safe-area-inset-bottom,0px))]';

  const footerSurfaceClass =
    'border-t border-border/60 bg-muted/35 mt-auto';

  if (variant === 'simple') {
    return (
      <footer className={`${footerSurfaceClass} ${footerSafeBottom}`}>
        <div className={`mx-auto px-4 py-4 ${shellClass || 'w-full'}`}>
          <div className="text-center">
            <div className="text-sm text-muted-foreground">{copyright}</div>
          </div>
        </div>
      </footer>
    );
  }

  if (variant === 'compact') {
    return (
      <footer className={`${footerSurfaceClass} ${footerSafeBottom}`}>
        <div className={`mx-auto px-4 sm:px-6 lg:px-8 py-8 ${shellClass || 'w-full'}`}>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
            {brandSlot ? <div className="flex items-center gap-3">{brandSlot}</div> : null}

            {links.length > 0 && (
              <div className="flex flex-wrap items-center justify-center gap-6">
                {links.map((link) =>
                  link.external ? (
                    <a
                      key={link.path}
                      href={link.path}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`text-sm text-muted-foreground hover:text-foreground transition-colors ${FOOTER_LINK_TOUCH}`}
                    >
                      {link.label}
                    </a>
                  ) : (
                    <Link
                      key={link.path}
                      href={link.path}
                      className={`text-sm text-muted-foreground hover:text-foreground transition-colors ${FOOTER_LINK_TOUCH}`}
                    >
                      {link.label}
                    </Link>
                  )
                )}
              </div>
            )}
          </div>

          <div className="mt-6 pt-6 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-muted-foreground">
            <span>{copyright}</span>
            {credits && (
              credits.url ? (
                <a
                  href={credits.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  {credits.text}
                </a>
              ) : (
                <span>{credits.text}</span>
              )
            )}
          </div>
        </div>
      </footer>
    );
  }

  return (
    <>
      <footer className={`lg:hidden ${footerSurfaceClass} ${footerSafeBottom}`}>
        <div className={`mx-auto px-4 py-8 ${shellClass || 'w-full'}`}>
          {/*
            The mobile footer is a centered stack — links, copyright and the
            control row all center themselves. The brand has to be centered
            HERE rather than by the caller: `FooterProjectInfo variant="mobile"`
            centers itself, so a consumer passing `brand.slot` used to be the
            only thing in the column left-aligned, reading as a mistake rather
            than a choice. The wrapper also owns the gap to the links below,
            which the bare slot had no way to provide.
          */}
          {showBrandColumn && (
            brandSlot ? (
              <div className="mb-6 flex justify-center">{brandSlot}</div>
            ) : (
              <FooterProjectInfo
                description={description}
                socialLinks={socialLinks}
                variant="mobile"
              />
            )
          )}

          {links.length > 0 && (
            <div className="flex flex-wrap justify-center gap-3 mb-6">
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

          <div className="border-t border-border mt-6 pt-4 space-y-3">
            <div className="text-xs text-muted-foreground text-center">{copyright}</div>
            {credits && (
              <div className="text-xs text-muted-foreground text-center">
                {credits.url ? (
                  <a href={credits.url} target="_blank" rel="noopener noreferrer" className={`hover:text-foreground transition-colors ${FOOTER_LINK_TOUCH}`}>
                    {credits.text}
                  </a>
                ) : (
                  credits.text
                )}
              </div>
            )}
          </div>

          {showFooterControlsRow && (
            <div className="mt-5 flex items-center justify-center gap-2 border-t border-border/60 pt-4">
              {showThemeSwitcher && <ThemeModeControl />}
              {showLocaleSwitcher && (
                <LocaleSwitcher
                  buttonVariant="outline"
                  size="default"
                  className="h-10 rounded-full border-border/60 bg-muted/30 text-sm hover:bg-muted/40"
                />
              )}
            </div>
          )}
        </div>
      </footer>
      <footer className={`max-lg:hidden ${footerSurfaceClass} ${footerSafeBottom}`}>
        <div className={`mx-auto px-6 sm:px-8 lg:px-10 py-14 ${shellClass || 'w-full'}`}>
          {slots?.aboveMenus && <div className="mb-10">{slots.aboveMenus}</div>}

          <div className="grid grid-cols-12 gap-10 lg:gap-14">
            {showBrandColumn && (
              <div className="col-span-12 lg:col-span-4">
                {brandSlot ?? (
                  <FooterProjectInfo
                    description={description}
                    badge={badge}
                    socialLinks={socialLinks}
                    variant="desktop"
                  />
                )}
              </div>
            )}

            <div className={showBrandColumn ? 'col-span-12 lg:col-span-8 lg:pl-8' : 'col-span-12'}>
              <FooterMenuSections
                menuSections={menuSections}
                minColumnWidth={menuColumnMinWidth}
                maxColumns={menuMaxColumns}
              />
            </div>
          </div>

          {slots?.belowMenus && <div className="mt-10">{slots.belowMenus}</div>}

          <div
            className={
              showFooterControlsRow
                ? 'mt-12 grid grid-cols-1 items-center gap-4 border-t border-border/60 pt-5 lg:grid-cols-[1fr_auto_1fr] lg:gap-6'
                : 'mt-12 flex flex-col gap-4 border-t border-border/60 pt-5 lg:flex-row lg:items-center lg:justify-between'
            }
          >
            <div className="flex min-w-0 flex-wrap items-center justify-center gap-3 text-center text-xs text-muted-foreground lg:justify-self-start lg:text-left">
              <span className="whitespace-nowrap">{copyright}</span>
              {slots?.bottomStart}
            </div>

            <div className="flex min-w-0 flex-wrap items-center justify-center gap-3 text-center text-xs text-muted-foreground lg:justify-self-center">
              {credits && (
                credits.url ? (
                  <a href={credits.url} target="_blank" rel="noopener noreferrer" className={`hover:text-foreground transition-colors whitespace-nowrap ${FOOTER_LINK_TOUCH}`}>
                    {credits.text}
                  </a>
                ) : (
                  <span className="whitespace-nowrap">{credits.text}</span>
                )
              )}
              {links.length > 0 && links.map((link) =>
                link.external ? (
                  <a
                    key={link.path}
                    href={link.path}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`hover:text-foreground transition-colors whitespace-nowrap ${FOOTER_LINK_TOUCH}`}
                  >
                    {link.label}
                  </a>
                ) : (
                  <Link key={link.path} href={link.path} className={`hover:text-foreground transition-colors whitespace-nowrap ${FOOTER_LINK_TOUCH}`}>
                    {link.label}
                  </Link>
                )
              )}
            </div>

            {(showFooterControlsRow || slots?.bottomEnd) && (
              <div className="flex items-center justify-center gap-2 lg:justify-self-end">
                {slots?.bottomEnd}
                {showThemeSwitcher && <ThemeModeControl />}
                {showLocaleSwitcher && (
                  <LocaleSwitcher
                    buttonVariant="outline"
                    size="default"
                    className="h-10 rounded-full border-border/60 bg-muted/30 text-sm hover:bg-muted/40"
                  />
                )}
              </div>
            )}
          </div>
        </div>
      </footer>
    </>
  );
}

/**
 * Memoised footer. Uses reference equality on `config` — the consumer is
 * expected to stabilise the config object (useMemo / useState). This avoids
 * deep-comparing large nested config trees while still preventing re-renders
 * when the same config object is passed through successive parent renders.
 */
export const DefaultFooter = memo(DefaultFooterRaw, (prev, next) => {
  return prev.config === next.config;
});
