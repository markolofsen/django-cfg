'use client';

import React from 'react';
import {
  CopyButton,
} from '@djangocfg/ui-core/components';

interface CopyActionProps {
  value: string;
  title?: string;
}

const BUTTON_CLASS = 'h-6 w-6 rounded-sm bg-muted/80 hover:bg-muted border border-border/50 backdrop-blur-sm';

export const CopyAction: React.FC<CopyActionProps> = ({ value, title = 'Copy' }) => (
  <CopyButton
    value={value}
    variant="ghost"
    size="icon"
    className={BUTTON_CLASS}
    iconClassName="h-3 w-3"
    tooltip={title}
  />
);
