'use client';

import React, { memo, useCallback, useMemo, useState } from 'react';

import {
  AUTH_CONSTANTS,
  endTwoFactorChallenge,
  useTwoFactorChallenge,
  useTwoFactorVerify,
} from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Input,
  OTPInput,
} from '@djangocfg/ui-core/components';

export interface TwoFactorChallengeDialogProps {
  /** Runs once the code is accepted and the session is stored. Without it the dialog navigates itself. */
  onVerified?: () => void;
  /** Runs when the user abandons the challenge. */
  onCancel?: () => void;
  /** Where the dialog navigates after success when `onVerified` is absent. */
  redirectUrl?: string;
}

/**
 * Second-factor prompt over whatever page started the sign-in.
 *
 * Opens when a sign-in step calls `beginTwoFactorChallenge` and owns everything
 * from there: code entry, backup-code fallback, lockout hints. The sign-in form
 * does not know it exists.
 */
function TwoFactorChallengeDialogRaw(props: TwoFactorChallengeDialogProps) {
  const challenge = useTwoFactorChallenge();
  const { onCancel } = props;

  const handleOpenChange = useCallback(
    (open: boolean) => {
      if (open) return;
      endTwoFactorChallenge();
      onCancel?.();
    },
    [onCancel],
  );

  return (
    <Dialog open={challenge !== null} onOpenChange={handleOpenChange}>
      {/* A stray click must not discard a verified password or email code. */}
      <DialogContent className="max-w-sm" onInteractOutside={(e) => e.preventDefault()}>
        {challenge && <Challenge key={challenge.sessionId} sessionId={challenge.sessionId} {...props} />}
      </DialogContent>
    </Dialog>
  );
}

function Challenge({
  sessionId,
  onVerified,
  redirectUrl,
}: TwoFactorChallengeDialogProps & { sessionId: string }) {
  const t = useAppT();
  const [code, setCode] = useState('');
  const [useBackupCode, setUseBackupCode] = useState(false);

  const verify = useTwoFactorVerify({
    onSuccess: () => {
      endTwoFactorChallenge();
      onVerified?.();
    },
    redirectUrl,
    skipRedirect: Boolean(onVerified),
  });

  const content = useMemo(
    () => ({
      title: t('layouts.auth.twoFactor.title'),
      subtitle: {
        totp: t('layouts.auth.twoFactor.subtitle.totp'),
        backup: t('layouts.auth.twoFactor.subtitle.backup'),
      },
      placeholder: t('layouts.auth.twoFactor.placeholder.backup'),
      button: t('layouts.auth.twoFactor.button'),
      toggle: {
        toBackup: t('layouts.auth.twoFactor.toggle.toBackup'),
        toTotp: t('layouts.auth.twoFactor.toggle.toTotp'),
      },
    }),
    [t],
  );

  const { isLoading, error, warning, attemptsRemaining, verifyTOTP, verifyBackupCode, clearError } = verify;

  const switchMode = useCallback(() => {
    setUseBackupCode((prev) => !prev);
    setCode('');
    clearError();
  }, [clearError]);

  const handleTotpComplete = useCallback(
    (value: string) => {
      if (!isLoading) void verifyTOTP(sessionId, value);
    },
    [isLoading, sessionId, verifyTOTP],
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (isLoading) return;
      void (useBackupCode ? verifyBackupCode(sessionId, code) : verifyTOTP(sessionId, code));
    },
    [code, isLoading, sessionId, useBackupCode, verifyBackupCode, verifyTOTP],
  );

  const canSubmit = useBackupCode ? code.length > 0 : code.length === AUTH_CONSTANTS.TOTP_LENGTH;

  return (
    <>
      <DialogHeader>
        <DialogTitle>{content.title}</DialogTitle>
        <DialogDescription>
          {useBackupCode ? content.subtitle.backup : content.subtitle.totp}
        </DialogDescription>
      </DialogHeader>

      <form onSubmit={handleSubmit} className="space-y-4">
        {useBackupCode ? (
          <Input
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            placeholder={content.placeholder}
            disabled={isLoading}
            maxLength={AUTH_CONSTANTS.BACKUP_CODE_MAX_LENGTH}
            autoComplete="off"
            autoFocus
          />
        ) : (
          <div className="flex justify-center">
            <OTPInput
              length={AUTH_CONSTANTS.TOTP_LENGTH}
              validationMode="numeric"
              pasteBehavior="clean"
              value={code}
              onChange={setCode}
              onComplete={handleTotpComplete}
              disabled={isLoading}
              autoFocus
            />
          </div>
        )}

        {warning && <p className="text-sm text-muted-foreground">{warning}</p>}
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        {attemptsRemaining !== null && attemptsRemaining <= 3 && (
          <p className="text-sm text-muted-foreground">
            {attemptsRemaining} attempt{attemptsRemaining === 1 ? '' : 's'} remaining
          </p>
        )}

        <Button type="submit" className="w-full" disabled={!canSubmit || isLoading}>
          {content.button}
        </Button>

        <Button
          type="button"
          variant="link"
          className="w-full"
          onClick={switchMode}
          disabled={isLoading}
        >
          {useBackupCode ? content.toggle.toTotp : content.toggle.toBackup}
        </Button>
      </form>
    </>
  );
}

export const TwoFactorChallengeDialog = memo(TwoFactorChallengeDialogRaw);
