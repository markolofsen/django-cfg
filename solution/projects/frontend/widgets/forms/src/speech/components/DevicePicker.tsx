'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { MicDevice } from '../hooks/useMicDevices';

export interface DevicePickerProps {
  devices: MicDevice[];
  value: string | null;
  onChange: (id: string | null) => void;
  className?: string;
  disabled?: boolean;
  defaultLabel?: string;
  ariaLabel?: string;
}

export function DevicePicker({
  devices,
  value,
  onChange,
  className,
  disabled,
  defaultLabel = 'System default',
  ariaLabel = 'Microphone',
}: DevicePickerProps): React.ReactElement {
  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value || null)}
      disabled={disabled}
      aria-label={ariaLabel}
      className={cn(
        'h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
    >
      <option value="">{defaultLabel}</option>
      {devices.map((d) => (
        <option key={d.deviceId} value={d.deviceId}>
          {d.label}
        </option>
      ))}
    </select>
  );
}
