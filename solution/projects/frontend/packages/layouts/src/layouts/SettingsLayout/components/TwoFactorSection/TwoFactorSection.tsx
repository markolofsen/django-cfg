'use client';

import { Loader2, ShieldOff } from 'lucide-react';
import React, { useEffect, useState } from 'react';

import { useTwoFactorSetup, useTwoFactorStatus } from '@djangocfg/api/auth';
import {
  Alert,
  AlertDescription,
  Button,
  OTPInput,
  SettingRow,
  SettingsBlock,
} from '@djangocfg/ui-core/components';

import { fill, useSettingsCopy, type SettingsCopy } from '../../i18n';
import { TwoFactorSetupDialog } from './TwoFactorSetupDialog';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────────
// Disable confirmation — inline, not a dialog. Settings already lives in a
// dialog; stacking a second modal on top fights its focus trap and dims the
// context the user needs. Destructive confirmation expands in place instead
// (progressive disclosure), so the device list stays visible while confirming.
// ─────────────────────────────────────────────────────────────────────────────

function DisableConfirm({
  isLoading,
  error,
  onConfirm,
  onCancel,
}: {
  isLoading: boolean;
  error: string | null;
  onConfirm: (code: string) => void;
  onCancel: () => void;
}) {
  // Mounted fresh each time the confirmation opens — state starts clean.
  const copy = useSettingsCopy().security;
  const [code, setCode] = useState('');

  return (
    <div className="mt-3 space-y-4 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
      <div className="flex gap-2.5">
        <ShieldOff className="mt-0.5 h-4 w-4 flex-shrink-0 text-destructive" />
        <div className="space-y-1">
          <p className="text-sm font-medium">{copy.disableTitle}</p>
          <p className="text-[13px] leading-relaxed text-muted-foreground">
            {copy.disableHint}
          </p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <OTPInput
          length={6}
          validationMode="numeric"
          pasteBehavior="clean"
          value={code}
          onChange={setCode}
          disabled={isLoading}
          autoFocus
        />
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={isLoading}>
            {copy.cancel}
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => onConfirm(code)}
            disabled={isLoading || code.length !== 6}
          >
            {isLoading ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{copy.disabling}</>
            ) : (
              copy.disable
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function deviceDescription(copy: SettingsCopy['security'], createdAt: string, isPrimary: boolean): string {
  const added = fill(copy.deviceAdded, { date: new Date(createdAt).toLocaleDateString() });
  return isPrimary ? `${added} · ${copy.devicePrimary}` : added;
}

// ─────────────────────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────────────────────

export const TwoFactorSection: React.FC = () => {
  const copy = useSettingsCopy().security;
  const [setupOpen, setSetupOpen] = useState(false);
  const [showDisable, setShowDisable] = useState(false);

  const {
    isLoading,
    error,
    has2FAEnabled,
    devices,
    fetchStatus,
    disable2FA,
    clearError,
  } = useTwoFactorStatus();

  const { resetSetup } = useTwoFactorSetup();

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const handleEnableClick = () => {
    resetSetup();
    setSetupOpen(true);
  };

  const handleSetupDone = () => {
    setSetupOpen(false);
    fetchStatus();
  };

  const handleDisableConfirm = async (code: string) => {
    const ok = await disable2FA(code);
    if (ok) setShowDisable(false);
  };

  const handleDisableCancel = () => {
    setShowDisable(false);
    clearError();
  };

  // ── Status view ─────────────────────────────────────────────────────────────
  // One compact block: a single status row (state + action), the inline confirm
  // when turning off, then the connected devices as plain rows.
  const unknown = has2FAEnabled === null;
  const statusDescription = unknown
    ? isLoading ? copy.checking : copy.unavailable
    : has2FAEnabled
      ? copy.on
      : copy.off;

  const statusAction = has2FAEnabled ? (
    <Button
      variant="outline"
      size="sm"
      onClick={() => { clearError(); setShowDisable(true); }}
      disabled={isLoading || showDisable}
    >
      {copy.turnOff}
    </Button>
  ) : (
    <Button size="sm" onClick={handleEnableClick} disabled={isLoading || unknown}>
      {copy.turnOn}
    </Button>
  );

  return (
    <SettingsBlock title={copy.title}>
      <SettingRow
        label={copy.twoFactor}
        description={statusDescription}
        action={statusAction}
      />

      {showDisable && (
        <DisableConfirm
          isLoading={isLoading}
          error={error}
          onConfirm={handleDisableConfirm}
          onCancel={handleDisableCancel}
        />
      )}

      {error && !showDisable && (
        <p className="py-2 text-[13px] text-destructive">{error}</p>
      )}

      {has2FAEnabled && devices.map((device) => (
        <SettingRow
          key={device.id}
          label={device.name}
          description={deviceDescription(copy, device.createdAt, device.isPrimary)}
        />
      ))}

      <TwoFactorSetupDialog
        open={setupOpen}
        onOpenChange={(open) => {
          setSetupOpen(open);
          // Closing mid-way or after finishing: the status row must reflect the server.
          if (!open) fetchStatus();
        }}
        onComplete={handleSetupDone}
      />
    </SettingsBlock>
  );
};
