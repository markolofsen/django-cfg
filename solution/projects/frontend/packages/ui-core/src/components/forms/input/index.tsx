import * as React from 'react';

import { useStoredValue, type StorageType, type UseStoredValueOptions } from '../../../hooks';
import { cn } from '../../../lib/utils';
import { fieldSizeClass, type FieldControlSize } from '../control-size';

export interface InputProps extends React.ComponentProps<"input"> {
  /**
   * When provided, the input value is persisted to storage under this key.
   *
   * Rules:
   * - If the parent passes `value` (controlled), storage is used for initial
   *   hydration only on first mount (defaultValue path is not applicable), but
   *   writes are still saved so the next mount can restore the value.
   *   In fully controlled mode the parent owns the value — storage just seeds
   *   the `defaultValue` on next fresh mount if the parent doesn't supply one.
   * - If the parent passes `defaultValue` or neither, the component is
   *   uncontrolled — storage provides the default and tracks changes via
   *   an onChange wrapper.
   *
   * @example storageKey="search-filter"
   */
  storageKey?: string;
  /**
   * Which storage backend to use.
   * @default 'local'
   */
  storageType?: StorageType;
  /**
   * TTL in ms. Stored value expires after this duration.
   */
  storageTtl?: number;
  /**
   * Control height, from the shared ladder in `forms/control-size.ts` — the
   * same name gives a `Button` and a `SelectTrigger` the same height.
   * - `xs` — 28px.
   * - `sm` — 32px.
   * - `default` — 36px.
   * - `lg` — 44px.
   */
  inputSize?: FieldControlSize;
  /**
   * Drop the field chrome — border, surface, rounding, focus ring — for an
   * input that sits inside a control that draws them itself (`InputGroup`).
   *
   * A wrapper cannot do this from the outside: `focus-visible:ring-0` and
   * `focus-visible:ring-1` are the same specificity, so which one wins is
   * decided by their order in the generated stylesheet, not by the order they
   * are passed to `cn()`. Suppression like that works until a Tailwind version
   * reorders its output. Omitting the rules is the only stable way to not have
   * them.
   */
  bare?: boolean;
}

/**
 * Shared input styling — single source so controlled/uncontrolled branches
 * stay identical.
 *
 * Surface: `bg-input` (a token a notch off the page/panel) instead of
 * `bg-transparent`, so the field reads as a real input on any surface (cards,
 * dialogs) rather than a near-black hole.
 *
 * Focus: a CRISP thin accent outline — the border turns the `--ring` colour
 * and a tight 1px solid ring of the same colour doubles it to a clean ~2px
 * edge (NO blurry translucent halo). `:focus-visible` only, so mouse users on
 * other controls don't get rings. This is the sharp Vercel/Linear look.
 *
 * Split in two so an input inside `InputGroup` can omit the chrome rather than
 * override it — see `bare`.
 */
/** Everything an input needs regardless of who draws its edge. */
const INPUT_CORE =
  "flex w-full transition-[color,background-color,border-color,box-shadow] file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50";

/** The field's own edge: border, surface, rounding, and the focus treatment. */
const INPUT_CHROME =
  "rounded-[var(--radius)] border border-border bg-input shadow-sm focus-visible:border-ring focus-visible:ring-1 focus-visible:ring-ring";

const INPUT_BASE = cn(INPUT_CORE, INPUT_CHROME);

const INPUT_SIZE: Record<NonNullable<InputProps['inputSize']>, string> = {
  xs: fieldSizeClass('xs'),
  sm: fieldSizeClass('sm'),
  default: fieldSizeClass('default'),
  lg: fieldSizeClass('lg'),
};

/** Resolve the full input class for a given size. */
export const inputClass = (
  size: NonNullable<InputProps['inputSize']> = 'default',
  bare = false,
) => cn(bare ? INPUT_CORE : INPUT_BASE, INPUT_SIZE[size], bare && 'h-full px-0');

/** Default-size input styling — kept as a named export for reuse (e.g. Editable). */
export const INPUT_CLASS = inputClass('default');

/**
 * Textarea styling — shares the SAME border/surface/focus base as inputs (one
 * source of truth) with multi-line height/padding instead of a fixed height.
 */
export const TEXTAREA_CLASS = cn(INPUT_BASE, 'min-h-[60px] px-3 py-2 text-base md:text-sm');

/** `TEXTAREA_CLASS` without the field's own edge — for use inside `InputGroup`. */
export const TEXTAREA_BARE_CLASS = cn(INPUT_CORE, 'min-h-[60px] py-3 text-base md:text-sm');

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, storageKey, storageType, storageTtl, inputSize = 'default', bare = false, onChange, defaultValue, value, ...props }, ref) => {
    const resolvedClass = cn(inputClass(inputSize, bare), className);
    const storageOptions: UseStoredValueOptions | undefined =
      storageKey ? { storage: storageType ?? 'local', ttl: storageTtl } : undefined;

    const [storedValue, setStoredValue] = useStoredValue<string>(
      storageKey,
      // seed: use provided defaultValue or controlled value as fallback seed
      (defaultValue as string | undefined) ?? (value as string | undefined) ?? '',
      storageOptions,
    );

    // Wrap onChange to persist to storage on every change.
    // Only active when storageKey is provided.
    const handleChange = React.useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        if (storageKey) {
          setStoredValue(e.target.value);
        }
        onChange?.(e);
      },
      [storageKey, setStoredValue, onChange],
    );

    // If parent passes explicit `value` — fully controlled, we don't inject
    // defaultValue (React would warn about switching modes). We still write
    // to storage on change via handleChange.
    if (value !== undefined) {
      return (
        <input
          type={type}
          className={resolvedClass}
          ref={ref}
          value={value}
          onChange={storageKey ? handleChange : onChange}
          {...props}
        />
      );
    }

    // Uncontrolled: inject stored value as defaultValue (if no defaultValue given).
    // React requires defaultValue to be stable on first render — storedValue from
    // useLocalStorage is initialValue on SSR and the real value after hydration.
    // This is fine: defaultValue only seeds the initial DOM value.
    return (
      <input
        type={type}
        className={resolvedClass}
        ref={ref}
        defaultValue={storageKey && storedValue ? storedValue : defaultValue}
        onChange={storageKey ? handleChange : onChange}
        {...props}
      />
    );
  },
);
Input.displayName = "Input"

export { Input }
