/**
 * ErrorButtons - Universal copy buttons for all error types
 *
 * Provides copy functionality for validation, CORS, and network errors
 */

'use client';

import { Copy, Terminal } from 'lucide-react';
import React from 'react';

import { Button } from '@djangocfg/ui-core';
import { useCopy } from '@djangocfg/ui-core/hooks';

import { generateCurlFromError } from '../utils/curl-generator';
import {
    formatCORSErrorForClipboard,
    formatNetworkErrorForClipboard,
    formatValidationErrorForClipboard
} from '../utils/formatters';

import type { ValidationErrorDetail, CORSErrorDetail, NetworkErrorDetail } from '../types';
export interface ErrorButtonsProps {
  detail: ValidationErrorDetail | CORSErrorDetail | NetworkErrorDetail;
}

/**
 * Format error for clipboard based on type
 */
function formatErrorForClipboard(detail: ValidationErrorDetail | CORSErrorDetail | NetworkErrorDetail): string {
  switch (detail.type) {
    case 'validation':
      return formatValidationErrorForClipboard(detail);
    case 'cors':
      return formatCORSErrorForClipboard(detail);
    case 'network':
      return formatNetworkErrorForClipboard(detail);
    default:
      return JSON.stringify(detail, null, 2);
  }
}

/**
 * Check if error supports cURL generation
 */
function supportsCurl(detail: ValidationErrorDetail | CORSErrorDetail | NetworkErrorDetail): boolean {
  return detail.type === 'validation';
}

/**
 * Universal error buttons
 */
export function ErrorButtons({ detail }: ErrorButtonsProps) {
  const { copyToClipboard } = useCopy();

  const handleCopyError = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const formattedError = formatErrorForClipboard(detail);
    await copyToClipboard(formattedError, '✅ Error details copied');
  };

  const handleCopyCurl = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (detail.type === 'validation') {
      const curl = generateCurlFromError({
        method: detail.method,
        path: detail.path,
        response: detail.response,
      });
      await copyToClipboard(curl, '✅ cURL command copied');
    }
  };

  return (
    <div className="flex gap-2 mt-2">
      <Button
        size="sm"
        variant="secondary"
        onClick={handleCopyError}
        className="text-xs bg-background hover:bg-background/80 text-foreground border border-border gap-1.5"
      >
        <Copy className="h-3.5 w-3.5" />
        Copy Error
      </Button>

      {supportsCurl(detail) && (
        <Button
          size="sm"
          variant="secondary"
          onClick={handleCopyCurl}
          className="text-xs bg-background hover:bg-background/80 text-foreground border border-border gap-1.5"
        >
          <Terminal className="h-3.5 w-3.5" />
          Copy cURL
        </Button>
      )}
    </div>
  );
}
