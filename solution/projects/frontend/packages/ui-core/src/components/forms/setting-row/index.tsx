'use client';

/**
 * SettingRow — the universal settings line, macOS / Claude-settings style:
 *
 *   [ label (+ description) ] ················· [ control ]
 *
 * separated from siblings by a single hairline (`--divider` token) — no card
 * frame. This is the canonical building block for any settings surface (the
 * SettingsLayout in @djangocfg/layouts is just one consumer).
 *
 * Props-driven control modes (precedence top→bottom):
 *   - `value` + `editable` + `onSave`  → inline-editable chip (text/phone)
 *   - `value`                          → read-only value chip
 *   - `toggle` + `onToggle`            → Switch
 *   - `navigation` (+ onClick)         → full-row button with a trailing chevron
 *   - `action`                         → right-aligned node (button/link)
 *   - `children`                       → arbitrary control (select, segmented…)
 *
 * Styling uses ONLY design tokens / ui-core primitives (Input, Switch) — no
 * arbitrary one-off classes — so it stays consistent and themeable everywhere.
 */

import * as React from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { parsePhoneNumberFromString } from 'libphonenumber-js';

import { cn } from '../../../lib/utils';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../../navigation/collapsible';
import { Editable, EditableInput, EditablePreview } from '../editable';
import { PhoneInput } from '../phone-input';
import { Switch } from '../switch';

function formatPhone(raw: string): string {
  if (!raw) return '';
  try {
    return parsePhoneNumberFromString(raw)?.formatInternational() ?? raw;
  } catch {
    return raw;
  }
}

/** Read-only / preview value chip — recessed `muted` fill, right-aligned. */
const VALUE_CHIP =
  'rounded-control inline-flex min-w-[7rem] items-center justify-end bg-muted px-3 py-1.5 text-right text-sm text-foreground';

export interface SettingRowProps {
  /** Left-hand label. */
  label: React.ReactNode;
  /** Optional helper text under the label (muted, small). May contain links. */
  description?: React.ReactNode;

  // ── Control modes ──
  /** Display a value (read-only chip, or inline-editable with `editable`). */
  value?: string;
  /** Make `value` inline-editable (Editable for text, PhoneInput for phone). */
  editable?: boolean;
  /** Commit handler for editable values. */
  onSave?: (value: string) => Promise<void> | void;
  /** Placeholder for an empty editable value. */
  placeholder?: string;
  /** Value kind — phone uses the country-aware input + formatting. */
  type?: 'text' | 'phone';
  /** Toggle mode — renders a Switch. */
  toggle?: boolean;
  /** Toggle state (with `toggle`). */
  checked?: boolean;
  /** Toggle change handler (with `toggle`). */
  onToggle?: (checked: boolean) => void;
  /** Navigation mode — whole row is a button with a trailing chevron. */
  navigation?: boolean;
  /** Right-aligned action node (button, link). */
  action?: React.ReactNode;
  /** Arbitrary right-hand control (select, segmented, custom). */
  children?: React.ReactNode;

  // ── Layout ──
  /** Stack the control under the label (wide inputs, textareas). */
  stacked?: boolean;
  /** Row click (also used by `navigation`). */
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export const SettingRow = React.forwardRef<HTMLDivElement, SettingRowProps>(
  (
    {
      label,
      description,
      value,
      editable = false,
      onSave,
      placeholder,
      type = 'text',
      toggle = false,
      checked,
      onToggle,
      navigation = false,
      action,
      children,
      stacked = false,
      onClick,
      disabled,
      className,
    },
    ref,
  ) => {
    const control = resolveControl({
      value, editable, onSave, placeholder, type,
      toggle, checked, onToggle, action, children, disabled,
    });

    const labelBlock = (
      <div className={cn('min-w-0', stacked ? 'w-full' : 'flex-1')}>
        <div className="text-sm text-foreground">{label}</div>
        {description && (
          // `div`, not `p`: `description` is arbitrary ReactNode and consumers
          // legitimately embed block-level nodes (e.g. a `<Badge>` status pill,
          // which renders a `<div>`) — a `<p>` cannot contain a `<div>` and
          // triggers an invalid-nesting hydration error.
          <div className="mt-0.5 text-[13px] leading-relaxed text-muted-foreground">{description}</div>
        )}
      </div>
    );

    const base = cn(
      'divider-b py-3.5',
      stacked ? 'block' : 'flex items-center justify-between gap-4',
      className,
    );

    // Navigation row: the entire row is a button with a trailing chevron.
    if (navigation) {
      return (
        <button
          type="button"
          onClick={onClick}
          disabled={disabled}
          className={cn(
            base,
            'group w-full rounded-control text-left transition-colors',
            disabled ? 'cursor-default opacity-60' : 'hover:bg-accent/50',
          )}
        >
          {labelBlock}
          <ChevronRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
        </button>
      );
    }

    // Clickable (non-navigation) row.
    if (onClick) {
      return (
        <button
          type="button"
          onClick={onClick}
          disabled={disabled}
          ref={ref as never}
          className={cn(
            base,
            'w-full text-left transition-colors',
            disabled ? 'cursor-default opacity-60' : 'hover:bg-accent/40',
          )}
        >
          {labelBlock}
          {control != null && <div className="flex shrink-0 items-center">{control}</div>}
        </button>
      );
    }

    return (
      <div ref={ref} className={base}>
        {labelBlock}
        {control != null && (
          <div className={cn('shrink-0', stacked ? 'mt-3 w-full' : 'flex items-center')}>{control}</div>
        )}
      </div>
    );
  },
);
SettingRow.displayName = 'SettingRow';

// ── Control resolver ──────────────────────────────────────────────────────────

interface ControlArgs {
  value?: string;
  editable: boolean;
  onSave?: (value: string) => Promise<void> | void;
  placeholder?: string;
  type: 'text' | 'phone';
  toggle: boolean;
  checked?: boolean;
  onToggle?: (checked: boolean) => void;
  action?: React.ReactNode;
  children?: React.ReactNode;
  disabled?: boolean;
}

function resolveControl(a: ControlArgs): React.ReactNode {
  if (a.toggle) {
    return <Switch checked={a.checked} onCheckedChange={a.onToggle} disabled={a.disabled} />;
  }
  if (a.value !== undefined && a.editable && a.onSave) {
    return (
      <EditableValue
        value={a.value}
        placeholder={a.placeholder ?? ''}
        type={a.type}
        onSave={a.onSave}
        disabled={a.disabled}
      />
    );
  }
  if (a.value !== undefined) {
    const text = a.value ? (a.type === 'phone' ? formatPhone(a.value) : a.value) : a.placeholder ?? '';
    return <span className={cn(VALUE_CHIP, !a.value && 'text-muted-foreground/60')}>{text}</span>;
  }
  if (a.action != null) return a.action;
  return a.children ?? null;
}

// ── Inline editable value ──────────────────────────────────────────────────────

interface EditableValueProps {
  value: string;
  placeholder: string;
  type: 'text' | 'phone';
  onSave: (value: string) => Promise<void> | void;
  disabled?: boolean;
}

function EditableValue({ value, placeholder, type, onSave, disabled }: EditableValueProps) {
  const submit = (next: string) => {
    if (next !== value) onSave(next);
  };

  if (type === 'phone') {
    return <PhoneEditable value={value} placeholder={placeholder} onSubmit={submit} disabled={disabled} />;
  }

  return (
    <Editable
      value={value}
      placeholder={placeholder}
      onValueSubmit={submit}
      readOnly={disabled}
      selectAllOnFocus
      submitOnBlur
      className="flex justify-end"
    >
      <EditablePreview
        className={cn(
          VALUE_CHIP,
          'cursor-text transition-colors hover:bg-accent',
          !value && 'text-muted-foreground/60',
          disabled && 'cursor-default opacity-60 hover:bg-muted',
        )}
      >
        {value || placeholder}
      </EditablePreview>
      {/* EditableInput renders the global Input styling at `sm` density. */}
      <EditableInput inputSize="sm" className="w-56" />
    </Editable>
  );
}

interface PhoneEditableProps {
  value: string;
  placeholder: string;
  onSubmit: (next: string) => void;
  disabled?: boolean;
}

function PhoneEditable({ value, placeholder, onSubmit, disabled }: PhoneEditableProps) {
  const [editing, setEditing] = React.useState(false);
  const [draft, setDraft] = React.useState(value);
  const wrapRef = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => setDraft(value), [value]);
  React.useEffect(() => {
    if (editing) wrapRef.current?.querySelector('input')?.focus();
  }, [editing]);

  if (!editing) {
    return (
      <button
        type="button"
        disabled={disabled}
        onClick={() => setEditing(true)}
        className={cn(VALUE_CHIP, 'transition-colors hover:bg-accent', !value && 'text-muted-foreground/60', disabled && 'opacity-60')}
      >
        {value ? formatPhone(value) : placeholder}
      </button>
    );
  }

  return (
    <div
      ref={wrapRef}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node)) {
          onSubmit(draft);
          setEditing(false);
        }
      }}
    >
      <PhoneInput value={draft} onChange={(v) => setDraft(v ?? '')} placeholder={placeholder} />
    </div>
  );
}

// ── Titled block of rows ────────────────────────────────────────────────────────

export interface SettingsBlockProps {
  /** Bold section heading (e.g. "Profile", "Preferences"). */
  title?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  /**
   * Make the whole block collapsible — the title becomes a clickable header
   * with a chevron, and the rows hide/reveal. Useful for rarely-needed or
   * destructive sections (e.g. "Danger zone"). Requires a `title`.
   */
  collapsible?: boolean;
  /** Initial open state when `collapsible`. Default: false. */
  defaultOpen?: boolean;
}

const BLOCK_TITLE = 'text-base font-medium text-foreground';

export const SettingsBlock: React.FC<SettingsBlockProps> = ({
  title,
  children,
  className,
  collapsible = false,
  defaultOpen = false,
}) => {
  if (collapsible && title) {
    return (
      <Collapsible defaultOpen={defaultOpen} className={cn('space-y-0', className)}>
        <CollapsibleTrigger
          className={cn(
            BLOCK_TITLE,
            'group flex w-full items-center gap-1.5 pb-1 transition-colors hover:text-foreground',
          )}
        >
          {title}
          <ChevronDown className="size-3.5 transition-transform duration-200 group-data-[state=open]:rotate-180" />
        </CollapsibleTrigger>
        <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down">
          <div>{children}</div>
        </CollapsibleContent>
      </Collapsible>
    );
  }

  return (
    <section className={cn('space-y-0', className)}>
      {title && <h2 className={cn(BLOCK_TITLE, 'pb-1')}>{title}</h2>}
      <div>{children}</div>
    </section>
  );
};
