/**
 * Header Component
 * Top header for mobile and page title with Copy for AI button
 */

'use client';

import React, { useState } from 'react';
import { Button, useIsMobile, useCopy } from '@djangocfg/ui';
import { Menu, X, Sparkles, Check } from 'lucide-react';

interface HeaderProps {
  title?: string;
  projectName?: string;
  logo?: React.ReactNode;
  isSidebarOpen?: boolean;
  onToggleSidebar?: () => void;
  onCopyForAI?: () => void;
}

export function Header({
  title = 'UI Component Library',
  projectName = 'Django CFG',
  logo,
  isSidebarOpen = false,
  onToggleSidebar,
  onCopyForAI,
}: HeaderProps) {
  const isMobile = useIsMobile();
  const { copyToClipboard } = useCopy();
  const [copied, setCopied] = useState(false);

  const handleCopyForAI = async () => {
    if (onCopyForAI) {
      onCopyForAI();
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      {/* Mobile Header - only on mobile */}
      {isMobile && (
        <header className="w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex h-14 items-center px-4 gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9"
              onClick={onToggleSidebar}
            >
              {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>

            <div className="flex items-center gap-2 flex-1">
              {logo}
              <span className="font-semibold text-sm">{projectName}</span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyForAI}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  <span className="hidden xs:inline">Copied!</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span className="hidden xs:inline">Copy for AI</span>
                </>
              )}
            </Button>
          </div>
        </header>
      )}

      {/* Desktop Page Header - only on desktop */}
      {!isMobile && (
        <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex h-14 items-center gap-4 px-6">
            <div className="flex-1">
              <h1 className="text-lg font-semibold">{title}</h1>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyForAI}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Copy for AI
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </>
  );
}
