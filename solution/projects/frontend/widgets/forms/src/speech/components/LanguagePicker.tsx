'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface LanguageOption {
  value: string;
  label: string;
}

const DEFAULT_LANGUAGES: LanguageOption[] = [
  { value: 'en-US', label: 'English (US)' },
  { value: 'en-GB', label: 'English (UK)' },
  { value: 'ru-RU', label: 'Русский' },
  { value: 'ko-KR', label: '한국어' },
  { value: 'ja-JP', label: '日本語' },
  { value: 'zh-CN', label: '中文 (简体)' },
  { value: 'es-ES', label: 'Español' },
  { value: 'fr-FR', label: 'Français' },
  { value: 'de-DE', label: 'Deutsch' },
];

export interface LanguagePickerProps {
  value: string;
  onChange: (value: string) => void;
  options?: LanguageOption[];
  className?: string;
  disabled?: boolean;
  ariaLabel?: string;
}

export function LanguagePicker({
  value,
  onChange,
  options = DEFAULT_LANGUAGES,
  className,
  disabled,
  ariaLabel = 'Recognition language',
}: LanguagePickerProps): React.ReactElement {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      aria-label={ariaLabel}
      className={cn(
        'h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

export { DEFAULT_LANGUAGES };
