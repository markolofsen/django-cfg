'use client';

import { Maximize2, Minimize2 } from 'lucide-react';
import React from 'react';

import { Button } from '@djangocfg/ui-core/components';

interface FullscreenActionProps {
  isFullscreen?: boolean;
  onToggle: () => void;
  title?: string;
}

const BUTTON_CLASS = 'h-6 w-6 rounded-sm bg-muted/80 hover:bg-muted border border-border/50 backdrop-blur-sm';

export const FullscreenAction: React.FC<FullscreenActionProps> = ({
  isFullscreen = false,
  onToggle,
  title,
}) => {
  const label = title ?? (isFullscreen ? 'Exit fullscreen' : 'Fullscreen');
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onToggle}
      aria-label={label}
      tooltip={label}
      className={BUTTON_CLASS}
    >
      {isFullscreen ? <Minimize2 className="h-3 w-3" /> : <Maximize2 className="h-3 w-3" />}
    </Button>
  );
};
