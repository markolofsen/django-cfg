import * as React from 'react';

import { useStoredValue, type StorageType, type UseStoredValueOptions } from '../../../hooks';
import { cn } from '../../../lib/utils';
import { TEXTAREA_BARE_CLASS, TEXTAREA_CLASS } from '../input';

export interface TextareaProps extends React.ComponentProps<"textarea"> {
  /**
   * When provided, the textarea value is persisted to storage under this key.
   * Same controlled/uncontrolled rules as Input.
   * @example storageKey="draft-message"
   */
  storageKey?: string;
  /** @default 'local' */
  storageType?: StorageType;
  /** TTL in ms */
  storageTtl?: number;
  /**
   * Drop the field chrome for a textarea inside a control that draws its own
   * (`InputGroup`). See `Input`'s `bare` for why this is a variant rather than
   * something a wrapper overrides.
   */
  bare?: boolean;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, storageKey, storageType, storageTtl, bare = false, onChange, defaultValue, value, ...props }, ref) => {
    const storageOptions: UseStoredValueOptions | undefined =
      storageKey ? { storage: storageType ?? 'local', ttl: storageTtl } : undefined;

    const [storedValue, setStoredValue] = useStoredValue<string>(
      storageKey,
      (defaultValue as string | undefined) ?? (value as string | undefined) ?? '',
      storageOptions,
    );

    const handleChange = React.useCallback(
      (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        if (storageKey) {
          setStoredValue(e.target.value);
        }
        onChange?.(e);
      },
      [storageKey, setStoredValue, onChange],
    );

    if (value !== undefined) {
      return (
        <textarea
          className={cn(bare ? TEXTAREA_BARE_CLASS : TEXTAREA_CLASS, className)}
          ref={ref}
          value={value}
          onChange={storageKey ? handleChange : onChange}
          {...props}
        />
      );
    }

    return (
      <textarea
        className={cn(bare ? TEXTAREA_BARE_CLASS : TEXTAREA_CLASS, className)}
        ref={ref}
        defaultValue={storageKey && storedValue ? storedValue : defaultValue}
        onChange={storageKey ? handleChange : onChange}
        {...props}
      />
    );
  },
);
Textarea.displayName = "Textarea"

export { Textarea }
