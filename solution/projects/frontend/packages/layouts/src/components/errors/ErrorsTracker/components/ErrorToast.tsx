/**
 * ErrorToast - Universal toast for all error types
 *
 * Formats validation, CORS, and network errors with appropriate styling
 */

'use client';

import React from 'react';

import { extractDomain, formatErrorTitle, formatZodIssues, safeZodIssues } from '../utils/formatters';
import { ErrorButtons } from './ErrorButtons';

import type {
  ValidationErrorDetail,
  CORSErrorDetail,
  NetworkErrorDetail,
  RuntimeErrorDetail,
  ValidationErrorConfig,
  CORSErrorConfig,
  NetworkErrorConfig,
  RuntimeErrorConfig,
} from '../types';
/**
 * Build validation error description
 */
function buildValidationDescription(
  detail: ValidationErrorDetail,
  config: Required<ValidationErrorConfig>
): React.ReactNode {
  const descriptionParts: string[] = [];

  // Add HTTP method and path
  if (config.showPath) {
    descriptionParts.push(`${detail.method} ${detail.path}`);
  }

  // Add error count
  if (config.showErrorCount) {
    const count = safeZodIssues(detail.error).length;
    if (count > 0) {
      const plural = count === 1 ? 'error' : 'errors';
      descriptionParts.push(`${count} ${plural}`);
    }
  }

  // Add formatted error messages
  const issuesText = formatZodIssues(detail.error, config.maxIssuesInToast);

  return (
    <div className="flex flex-col gap-2 text-sm">
      {descriptionParts.length > 0 && (
        <div className="font-mono text-xs opacity-90">
          {descriptionParts.join(' • ')}
        </div>
      )}
      <div className="opacity-90">{issuesText}</div>
      <ErrorButtons detail={detail} />
    </div>
  );
}

/**
 * Build CORS error description
 * Simplified: just show that server is unavailable, without CORS details
 */
function buildCORSDescription(
  detail: CORSErrorDetail,
  _config: Required<CORSErrorConfig>
): React.ReactNode {
  const domain = extractDomain(detail.url);

  return (
    <div className="flex flex-col gap-2 text-sm">
      <div className="opacity-90">
        Server {domain} is unavailable
      </div>

      <ErrorButtons detail={detail} />
    </div>
  );
}

/**
 * Build network error description
 */
function buildNetworkDescription(
  detail: NetworkErrorDetail,
  config: Required<NetworkErrorConfig>
): React.ReactNode {
  const parts: string[] = [];

  // Add method and URL info
  if (config.showMethod && config.showUrl) {
    parts.push(`${detail.method} ${detail.url}`);
  } else if (config.showUrl) {
    parts.push(detail.url);
  } else if (config.showMethod) {
    parts.push(`${detail.method} request failed`);
  }

  // Add status code
  if (config.showStatusCode && detail.statusCode) {
    parts.push(`Status: ${detail.statusCode}`);
  }

  return (
    <div className="flex flex-col gap-2 text-sm">
      {parts.length > 0 && (
        <div className="font-mono text-xs opacity-90">
          {parts.join(' • ')}
        </div>
      )}

      <div className="opacity-90">{detail.error}</div>

      <ErrorButtons detail={detail} />
    </div>
  );
}

/**
 * Build runtime error description
 */
function buildRuntimeDescription(
  detail: RuntimeErrorDetail,
  config: Required<RuntimeErrorConfig>
): React.ReactNode {
  return (
    <div className="flex flex-col gap-2 text-sm">
      {config.showSource && (
        <div className="font-mono text-xs opacity-90">
          Source: {detail.source}
        </div>
      )}

      <div className="opacity-90">{detail.message}</div>
    </div>
  );
}

/**
 * Create toast options for any error type
 */
export function createErrorToast(
  detail: ValidationErrorDetail | CORSErrorDetail | NetworkErrorDetail | RuntimeErrorDetail,
  config: Required<ValidationErrorConfig | CORSErrorConfig | NetworkErrorConfig | RuntimeErrorConfig>
) {
  let description: React.ReactNode;

  // Build description based on error type
  if (detail.type === 'validation') {
    description = buildValidationDescription(detail, config as Required<ValidationErrorConfig>);
  } else if (detail.type === 'cors') {
    description = buildCORSDescription(detail, config as Required<CORSErrorConfig>);
  } else if (detail.type === 'runtime') {
    description = buildRuntimeDescription(detail, config as Required<RuntimeErrorConfig>);
  } else {
    description = buildNetworkDescription(detail, config as Required<NetworkErrorConfig>);
  }

  return {
    title: formatErrorTitle(detail),
    description,
    variant: 'destructive' as const,
    duration: config.duration,
  };
}
