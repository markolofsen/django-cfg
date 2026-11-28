'use client';

import { Check, Copy } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import React, { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { AUTH_CONSTANTS, useTwoFactorSetup } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import {
  Alert,
  AlertDescription,
  Button,
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
  OTPInput,
  Preloader,
} from '@djangocfg/ui-core/components';

const QR_SIZE = 160;
const COPIED_MS = 2000;

export interface TwoFactorSetupProps {
  /** Runs when the user dismisses the backup codes — never earlier, or the codes are lost. */
  onComplete?: () => void;
  /** Shows a "skip" link on the QR step. */
  onSkip?: () => void;
}

function useCopy() {
  const [copied, setCopied] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current);
  }, []);

  const copy = useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      return;
    }
    setCopied(true);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setCopied(false), COPIED_MS);
  }, []);

  return { copied, copy };
}

/**
 * Enable 2FA: QR provisioning, confirmation code, then one-time backup codes.
 * Self-contained — no sign-in context — so any settings surface can mount it.
 */
function TwoFactorSetupRaw({ onComplete, onSkip }: TwoFactorSetupProps) {
  const t = useAppT();
  const { copied, copy } = useCopy();
  const [confirmCode, setConfirmCode] = useState('');

  const { isLoading, error, setupData, backupCodes, backupCodesWarning, setupStep, startSetup, confirmSetup } =
    useTwoFactorSetup({ onError: () => {} });

  useEffect(() => {
    if (setupStep === 'idle') void startSetup();
  }, [setupStep, startSetup]);

  const content = useMemo(
    () => ({
      loading: t('layouts.auth.setup.loading.button'),
      qr: {
        title: t('layouts.auth.setup.qrCode.title'),
        subtitle: t('layouts.auth.setup.qrCode.subtitle'),
        manualEntry: t('layouts.auth.setup.qrCode.manualEntry'),
        confirmPrompt: t('layouts.auth.setup.qrCode.confirmPrompt'),
        button: t('layouts.auth.setup.qrCode.button'),
        skip: t('layouts.auth.setup.qrCode.skip'),
      },
      done: {
        title: t('layouts.auth.setup.complete.title'),
        subtitle: t('layouts.auth.setup.complete.subtitle'),
        instruction: t('layouts.auth.setup.complete.instruction'),
        copyAll: t('layouts.auth.setup.complete.copyAll'),
        copied: t('layouts.auth.setup.complete.copied'),
        button: t('layouts.auth.setup.complete.done'),
      },
    }),
    [t],
  );

  const handleConfirm = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      void confirmSetup(confirmCode);
    },
    [confirmCode, confirmSetup],
  );

  if (setupStep === 'complete' && backupCodes) {
    return (
      <div className="w-full max-w-sm space-y-4">
        <Header title={content.done.title} subtitle={content.done.subtitle} />
        {backupCodesWarning && (
          <Alert>
            <AlertDescription>{backupCodesWarning}</AlertDescription>
          </Alert>
        )}
        <div className="grid grid-cols-2 gap-1.5 rounded-lg border border-dashed border-border bg-muted/40 p-3.5">
          {backupCodes.map((code) => (
            <code key={code} className="p-1.5 text-center font-mono text-[13px] tracking-wide">
              {code}
            </code>
          ))}
        </div>
        <p className="text-center text-sm text-muted-foreground">{content.done.instruction}</p>
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => void copy(backupCodes.join('\n'))}
        >
          {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
          {copied ? content.done.copied : content.done.copyAll}
        </Button>
        <Button type="button" className="w-full" onClick={() => onComplete?.()}>
          {content.done.button}
        </Button>
      </div>
    );
  }

  if (!setupData) {
    return <Preloader variant="inline" text={content.loading} className="py-4" />;
  }

  return (
    <form onSubmit={handleConfirm} className="w-full max-w-sm space-y-4">
      <Header title={content.qr.title} subtitle={content.qr.subtitle} />

      <div className="flex justify-center">
        {/* White plate: authenticator apps need dark-on-light contrast in both themes. */}
        <div className="rounded-lg bg-white p-3.5 shadow-sm">
          <QRCodeSVG value={setupData.provisioningUri} size={QR_SIZE} level="M" marginSize={0} />
        </div>
      </div>

      <Collapsible className="flex flex-col items-center">
        <CollapsibleTrigger asChild>
          <Button type="button" variant="link" size="sm">
            {content.qr.manualEntry}
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="flex flex-col items-center gap-2 p-3">
          <code className="break-all rounded bg-muted px-3.5 py-2 text-center font-mono text-[13px] tracking-wider">
            {setupData.secret}
          </code>
          <Button type="button" variant="link" size="sm" onClick={() => void copy(setupData.secret)}>
            {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
            {copied ? content.done.copied : 'Copy'}
          </Button>
        </CollapsibleContent>
      </Collapsible>

      <p className="text-center text-sm text-muted-foreground">{content.qr.confirmPrompt}</p>

      <div className="flex justify-center">
        <OTPInput
          length={AUTH_CONSTANTS.TOTP_LENGTH}
          validationMode="numeric"
          pasteBehavior="clean"
          value={confirmCode}
          onChange={setConfirmCode}
          disabled={isLoading}
        />
      </div>

      {error && (
        <p role="alert" className="text-center text-sm text-destructive">
          {error}
        </p>
      )}

      <Button
        type="submit"
        className="w-full"
        disabled={isLoading || confirmCode.length !== AUTH_CONSTANTS.TOTP_LENGTH}
      >
        {content.qr.button}
      </Button>

      {onSkip && (
        <Button type="button" variant="link" className="w-full" onClick={onSkip} disabled={isLoading}>
          {content.qr.skip}
        </Button>
      )}
    </form>
  );
}

function Header({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="space-y-1 text-center">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground">{subtitle}</p>
    </div>
  );
}

export const TwoFactorSetup = memo(TwoFactorSetupRaw);
