'use client';

import { useReducer } from 'react';

import { Button } from '@djangocfg/ui-core';

import { nextStep, type Step, type StepEvent } from './model';

/** 44px on touch. */
export const TOUCH = 'min-h-10 [@media(pointer:coarse)]:min-h-11';

interface Props {
  label: string;
  question: string;
  confirmLabel: string;
  keepLabel: string;
  /** Shown after a failed attempt. */
  failed: string;
  /** Resolves to whether it worked; the host announces the result. */
  onConfirm: () => Promise<boolean>;
}

/** An inline two-step, never `window.confirm`: the button asks, then confirms or keeps; a failure says so and offers it again. */
export function ConfirmAction({ label, question, confirmLabel, keepLabel, failed, onConfirm }: Props) {
  const [step, send] = useReducer((current: Step, event: StepEvent) => nextStep(current, event), 'idle');

  const confirm = async () => {
    send('start');
    send((await onConfirm()) ? 'done' : 'fail');
  };

  return (
    <div>
      {step === 'failed' ? (
        <span role="alert" className="mb-2 block text-sm leading-5 text-destructive">
          {failed}
        </span>
      ) : null}
      {step === 'asking' || step === 'busy' ? (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm leading-5 text-foreground">{question}</span>
          <Button type="button" size="sm" variant="destructive" className={TOUCH} disabled={step === 'busy'} onClick={() => void confirm()}>
            {confirmLabel}
          </Button>
          <Button type="button" size="sm" variant="ghost" className={TOUCH} disabled={step === 'busy'} onClick={() => send('keep')}>
            {keepLabel}
          </Button>
        </div>
      ) : (
        <Button type="button" size="sm" variant="outline" className={TOUCH} onClick={() => send('ask')}>
          {label}
        </Button>
      )}
    </div>
  );
}
