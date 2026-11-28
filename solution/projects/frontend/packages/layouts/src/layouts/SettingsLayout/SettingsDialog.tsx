'use client';

import React, { useCallback, useEffect, useMemo } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@djangocfg/ui-core/components';
import { useIsMobile } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';

import { SettingsForm } from './SettingsForm';
import { useGuestIntentRedirect } from './hooks/useGuestIntentRedirect';
import { useSettingsUrl } from './hooks/useSettingsUrl';
import { useSettingsCopy } from './i18n';
import { buildBuiltinSections } from './sections';
import { useSettingsDialogStore } from './store';
import type { SettingsDialogProps } from './types';

// Defaults must be module constants: a `= []` / `= {}` default is a new object each render, which would
// re-run every effect and memo below that lists it.
const NO_SECTIONS: NonNullable<SettingsDialogProps['sections']> = [];
const NO_BUILTINS: NonNullable<SettingsDialogProps['builtins']> = {};

/**
 * SettingsDialog — the globally-mounted settings modal.
 *
 * Mount once (PrivateLayout does this). Open it from anywhere via
 * `useSettingsDialog().open()` or by navigating to `#settings/<section>`.
 *
 * Reads transient state (open + active section) from the zustand store and
 * binds it to the controlled <SettingsForm>. When `syncUrl` (default) it also
 * two-way-binds that state to the URL hash via useSettingsUrl.
 */
export const SettingsDialog: React.FC<SettingsDialogProps> = ({
  syncUrl = true,
  urlKey = 'settings',
  title,
  sections: appSections = NO_SECTIONS,
  groups,
  builtins = NO_BUILTINS,
  generalRows,
  initialSection,
  searchable = 'auto',
  enableDeleteAccount = true,
}) => {
  const isOpen = useSettingsDialogStore((s) => s.isOpen);
  const activeSection = useSettingsDialogStore((s) => s.activeSection);
  const close = useSettingsDialogStore((s) => s.close);
  const setSection = useSettingsDialogStore((s) => s.setSection);
  const isMobile = useIsMobile();
  const copy = useSettingsCopy();
  // Settings are about the signed-in user: for a guest the panels are empty, so `#settings` opens nothing until sign-in.
  const { isAuthenticated } = useAuth();

  // Set of valid ids, so a bad URL hash falls back gracefully instead of
  // selecting a non-existent section. Cheap to recompute; built-ins are pure.
  const knownIds = useMemo(() => {
    const builtin = buildBuiltinSections({ builtins, enableDeleteAccount, copy });
    const ids = new Set<string>();
    [...builtin, ...appSections].forEach((s) => ids.add(s.id));
    return ids;
  }, [builtins, enableDeleteAccount, appSections, copy]);

  // Menus (the account menu) link to these; only this component knows the host's sections.
  const setMenuSections = useSettingsDialogStore((s) => s.setSections);
  useEffect(() => {
    const all = [...buildBuiltinSections({ builtins, enableDeleteAccount, copy }), ...appSections];
    setMenuSections(all.filter((s) => !s.hidden).map(({ id, label, icon }) => ({ id, label, icon })));
  }, [builtins, enableDeleteAccount, appSections, copy, setMenuSections]);

  const resolveSection = useCallback(
    (id: string | null) => (id && knownIds.has(id) ? id : null),
    [knownIds],
  );

  useSettingsUrl({ urlKey, enabled: syncUrl && isAuthenticated, resolveSection });
  useGuestIntentRedirect(urlKey ?? 'settings', syncUrl !== false);

  const resolvedTitle = title ?? copy.nav.title;

  return (
    <Dialog open={isOpen && isAuthenticated} onOpenChange={(open) => !open && close()}>
      <DialogContent
        // Desktop: large centred card, proportional to the viewport.
        // Mobile: near-fullscreen sheet (small inset) so the phone settings get
        // the whole screen, like Claude. Elevated `bg-card` lifts it off the page.
        className={cn(
          'flex max-w-none flex-col gap-0 overflow-hidden border border-foreground/5 bg-card p-0',
          isMobile
            ? 'h-[calc(100dvh-2rem)] w-[calc(100vw-1.5rem)]'
            // Claude proportions: 1024×800 at most, 1.28:1 at every size (ui-core
            // DialogContent derives the width from the viewport height).
            : '[--aspect-dialog:1.28] [--width-dialog:1024px]',
        )}
      >
        {/* Accessible label — the visible heading is the shell header bar. */}
        <DialogTitle className="sr-only">
          {typeof resolvedTitle === 'string' ? resolvedTitle : 'Settings'}
        </DialogTitle>
        <DialogDescription className="sr-only">
          Application settings
        </DialogDescription>

        <SettingsForm
          bare
          title={resolvedTitle}
          sections={appSections}
          groups={groups}
          builtins={builtins}
          generalRows={generalRows}
          initialSection={initialSection}
          searchable={searchable}
          enableDeleteAccount={enableDeleteAccount}
          activeSection={activeSection ?? undefined}
          onSectionChange={setSection}
        />
      </DialogContent>
    </Dialog>
  );
};
