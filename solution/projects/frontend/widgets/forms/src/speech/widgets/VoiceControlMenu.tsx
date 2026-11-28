'use client';

import type * as React from 'react';
import { useMemo, useState } from 'react';
import {
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Hand,
  Languages,
  Mic,
} from 'lucide-react';

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
  Switch,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { buildLanguageRows } from '@djangocfg/ui-core/lib/speech-language';
import { useMicDevices } from '../hooks/useMicDevices';
import { useMicLevel } from '../hooks/useMicLevel';
import { useMicPreview } from '../hooks/useMicPreview';
import { useSpeechLanguageInfo } from '../hooks/useSpeechLanguageInfo';
import { useSpeechPrefs } from '../store/prefsStore';
import { LanguageCommandList } from '../components/LanguageCommandList';
import { MicMeter } from '../components/MicMeter';

export interface VoiceControlMenuProps {
  /**
   * Subset of BCP-47 tags to offer in the language view. Default: the
   * full Web Speech catalogue. Pass a tighter list when a backend
   * engine only supports a subset; pass `[]` to hide the language row
   * entirely (server engines that detect language themselves).
   */
  allowedTags?: string[];
  /** Panel alignment relative to the trigger. @default 'end' */
  align?: 'start' | 'center' | 'end';
  /** Extra classes on the chevron trigger button. */
  className?: string;
}

/** Shared row shell — quiet, menu-like, full-width. */
const ROW_CLS = cn(
  'flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-sm',
  'transition-colors hover:bg-accent hover:text-accent-foreground',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
);

/**
 * The mic chevron menu — the companion control next to the composer mic
 * button (claude.ai reference, 2026-08-03): live level meter (the
 * instant "is my mic working" check on a short-lived preview stream),
 * input device list, a Language row, and a hold-to-record toggle.
 *
 * ONE Popover with two in-place views (main ⇄ language search), the
 * claude model-menu pattern. A menu that spawned a SECOND popover for
 * language search dismissed both at once — Radix menu close-on-select
 * and the new popover's outside-click fight each other, and a search
 * input inside a Radix menu loses keys to typeahead. In-place views
 * have neither problem.
 *
 * All state persists through `useSpeechPrefs`; the widget owns nothing.
 */
export function VoiceControlMenu({
  allowedTags,
  align = 'end',
  className,
}: VoiceControlMenuProps): React.ReactElement {
  const prefs = useSpeechPrefs();
  const language = useSpeechLanguageInfo();
  const { devices, refresh } = useMicDevices();

  // The preview stream lives only while the panel is open.
  const [open, setOpenState] = useState(false);
  const [view, setView] = useState<'main' | 'language'>('main');
  const setOpen = (v: boolean): void => {
    setOpenState(v);
    if (!v) setView('main');
  };
  const previewStream = useMicPreview(open, prefs.deviceId);
  const level = useMicLevel(previewStream);

  // Device labels are hidden until the page holds mic permission; the
  // preview stream IS that permission, so refresh once it arrives.
  const hasStream = previewStream !== null;
  const [refreshedFor, setRefreshedFor] = useState(false);
  if (hasStream !== refreshedFor) {
    setRefreshedFor(hasStream);
    if (hasStream) void refresh();
  }

  const showLanguageRow = useMemo(
    () => buildLanguageRows(allowedTags).length > 0,
    [allowedTags],
  );

  const currentLanguageLabel = language.name ?? language.tag;
  // The row always shows the CURRENT outcome and whether it was picked
  // automatically — the silent-wrong-language failure died here.
  const languageValueLabel = language.hasUserChoice
    ? currentLanguageLabel
    : `Auto · ${currentLanguageLabel}`;

  const activeDeviceId = prefs.deviceId;
  const deviceRows = [
    { id: null as string | null, label: 'System default' },
    ...devices.map((d) => ({ id: d.deviceId as string | null, label: d.label })),
  ];

  const mainView = (
    <div className="flex flex-col gap-0.5 p-1">
      <div className="flex items-center gap-2 px-2 py-1.5">
        <Mic className="size-4 shrink-0 text-muted-foreground" aria-hidden />
        <MicMeter level={level} bars={18} height={16} className="flex-1" />
      </div>
      <div className="-mx-1 my-0.5 h-px bg-border" />
      {deviceRows.map((d) => (
        <button
          key={d.id ?? '__default'}
          type="button"
          onClick={() => prefs.setDeviceId(d.id)}
          className={ROW_CLS}
        >
          <span className="min-w-0 flex-1 truncate">{d.label}</span>
          {activeDeviceId === d.id ? (
            <Check className="size-4 shrink-0 text-primary" aria-hidden />
          ) : null}
        </button>
      ))}
      {showLanguageRow ? (
        <>
          <div className="-mx-1 my-0.5 h-px bg-border" />
          <button
            type="button"
            onClick={() => setView('language')}
            className={ROW_CLS}
          >
            <Languages className="size-4 shrink-0 text-muted-foreground" aria-hidden />
            <span className="flex min-w-0 flex-1 flex-col">
              <span>Language</span>
              <span className="truncate text-xs text-muted-foreground">
                {languageValueLabel}
              </span>
            </span>
            <ChevronRight className="size-4 shrink-0 text-muted-foreground" aria-hidden />
          </button>
        </>
      ) : null}
      <div className="-mx-1 my-0.5 h-px bg-border" />
      {/*
        A `label`, not a `button`: `Switch` renders its own `<button role="switch">`,
        and a button inside a button is invalid HTML — the browser reparents it,
        which is why the contract suite reported a hydration error here. The row
        used to own the click and disable the switch (`pointer-events-none`,
        `tabIndex={-1}`), leaving the control unreachable by keyboard. Wrapping in
        a label keeps the whole row clickable and gives the switch its label back.
      */}
      <label className={cn(ROW_CLS, 'cursor-pointer')}>
        <Hand className="size-4 shrink-0 text-muted-foreground" aria-hidden />
        <span className="min-w-0 flex-1">Hold to record</span>
        <Switch
          checked={prefs.holdToRecord}
          onCheckedChange={prefs.setHoldToRecord}
        />
      </label>
    </div>
  );

  const languageView = (
    <div className="flex flex-col">
      <div className="flex items-center gap-1 border-b border-border px-1 py-1">
        <button
          type="button"
          onClick={() => setView('main')}
          aria-label="Back"
          className={cn(
            'inline-flex h-6 w-6 items-center justify-center rounded-sm',
            'text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          )}
        >
          <ChevronLeft className="size-4" aria-hidden />
        </button>
        <span className="text-sm font-medium">Language</span>
      </div>
      <LanguageCommandList
        allowedTags={allowedTags}
        onPick={() => setOpen(false)}
      />
    </div>
  );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          aria-label="Voice input options"
          className={cn(
            'inline-flex h-7 w-5 items-center justify-center rounded-md',
            'text-muted-foreground transition-colors',
            'hover:bg-accent hover:text-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            'data-[state=open]:bg-accent data-[state=open]:text-foreground',
            className,
          )}
        >
          <ChevronDown className="size-3.5" aria-hidden />
        </button>
      </PopoverTrigger>
      <PopoverContent side="top" align={align} className="w-64 p-0">
        {view === 'main' ? mainView : languageView}
      </PopoverContent>
    </Popover>
  );
}
