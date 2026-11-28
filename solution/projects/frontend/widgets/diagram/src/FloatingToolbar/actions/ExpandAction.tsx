'use client';

import { ChevronDown, ChevronUp } from 'lucide-react';
import React from 'react';

import { Button } from '@djangocfg/ui-core/components';

interface ExpandActionProps {
  isExpanded: boolean;
  onToggle: () => void;
}

const BUTTON_CLASS = 'h-6 w-6 rounded-sm bg-muted/80 hover:bg-muted border border-border/50 backdrop-blur-sm';

export const ExpandAction: React.FC<ExpandActionProps> = ({ isExpanded, onToggle }) => {
  const label = isExpanded ? 'Collapse All' : 'Expand All';
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onToggle}
      aria-label={label}
      tooltip={label}
      className={BUTTON_CLASS}
    >
      {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
    </Button>
  );
};
