'use client';

import { Download } from 'lucide-react';
import React from 'react';

import { Button } from '@djangocfg/ui-core/components';

interface DownloadActionProps {
  value: string;
  filename?: string;
  mimeType?: string;
  title?: string;
}

const BUTTON_CLASS = 'h-6 w-6 rounded-sm bg-muted/80 hover:bg-muted border border-border/50 backdrop-blur-sm';

export const DownloadAction: React.FC<DownloadActionProps> = ({
  value,
  filename = 'download.txt',
  mimeType = 'text/plain',
  title = 'Download',
}) => {
  const handleDownload = () => {
    const blob = new Blob([value], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleDownload}
      aria-label={title}
      tooltip={title}
      className={BUTTON_CLASS}
    >
      <Download className="h-3 w-3" />
    </Button>
  );
};
