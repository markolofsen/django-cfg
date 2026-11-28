'use client';

import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useT } from '@djangocfg/i18n';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../../../components/overlay/dialog';
import { Button } from '../../../components/forms/button';
import { Input } from '../../../components/forms/input';
import { useHotkey } from '../../../hooks';
import { I18N_KEYS } from '../constants';
import type { DialogOptions } from '../types';

interface PromptDialogUIProps {
  open: boolean;
  options: DialogOptions;
  onConfirm: (value: string) => void;
  onCancel: () => void;
}

export function PromptDialogUI({
  open,
  options,
  onConfirm,
  onCancel,
}: PromptDialogUIProps) {
  const t = useT();
  const [value, setValue] = useState(options.defaultValue || '');
  const inputRef = useRef<HTMLInputElement>(null);

  // Prepare data before render
  const dialogData = useMemo(() => ({
    title: options.title || t(I18N_KEYS.promptTitle),
    message: options.message,
    confirmText: options.confirmText || t(I18N_KEYS.ok),
    cancelText: options.cancelText || t(I18N_KEYS.cancel),
    placeholder: options.placeholder || t(I18N_KEYS.promptPlaceholder),
    inputType: options.inputType || 'text',
    preventClose: options.preventClose ?? false,
  }), [options, t]);

  // Reset value when dialog opens with new options
  useEffect(() => {
    if (open) {
      setValue(options.defaultValue || '');
      // Focus input after a short delay to ensure dialog is fully rendered
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open, options.defaultValue]);

  const handleSubmit = useCallback((e?: React.FormEvent) => {
    e?.preventDefault();
    onConfirm(value);
  }, [onConfirm, value]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
  }, []);

  const handleOpenChange = useCallback((isOpen: boolean) => {
    if (!isOpen && !dialogData.preventClose) {
      onCancel();
    }
  }, [dialogData.preventClose, onCancel]);

  // Hotkey: Escape to cancel (Enter is handled by form submit)
  useHotkey('escape', onCancel, { enabled: open });

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{dialogData.title}</DialogTitle>
            <DialogDescription>{dialogData.message}</DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              ref={inputRef}
              type={dialogData.inputType}
              value={value}
              onChange={handleChange}
              placeholder={dialogData.placeholder}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onCancel}>
              {dialogData.cancelText}
            </Button>
            <Button type="submit">
              {dialogData.confirmText}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
