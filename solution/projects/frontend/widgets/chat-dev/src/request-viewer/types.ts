// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';
import type { HttpMethodTone, HttpStatusTone } from './http';

/** Single key/value header pair. */
export interface HeaderEntry {
  name: string;
  value: string;
}

/** A timing phase for the request lifecycle (DNS, TCP, TLS, …). */
export interface TimingEntry {
  /** Label for this timing phase (e.g. "DNS Lookup", "TLS Handshake"). */
  label: string;
  /** Duration in milliseconds. */
  duration: number;
}

/**
 * A captured network request — already-executed. The viewer never fetches.
 */
export interface NetworkRequest {
  /** HTTP method (GET, POST, etc.). Case-insensitive. */
  method: string;
  /** Full request URL. */
  url: string;
  /** HTTP status code. */
  status: number;
  /** HTTP status text (e.g. "OK", "Not Found"). */
  statusText?: string;
  /** Request headers. */
  requestHeaders?: HeaderEntry[];
  /** Response headers. */
  responseHeaders?: HeaderEntry[];
  /** Response body as a string (raw text or JSON-encoded text). */
  responseBody?: string;
  /** Content type of the response (used for display hints). */
  contentType?: string;
  /** Timing breakdown for the request lifecycle. */
  timing?: TimingEntry[];
  /** Total request duration in milliseconds. */
  duration?: number;
}

export type RequestViewerTab = 'headers' | 'body' | 'timing';

export interface RequestViewerProps
  extends Omit<React.ComponentProps<'div'>, 'children'> {
  /** Network request data to display. */
  request: NetworkRequest;
  /** Initial active tab. Defaults to "headers". */
  defaultTab?: RequestViewerTab;
}

// Re-export the HTTP tone types for callers that need them.
export type { HttpMethodTone, HttpStatusTone };

/**
 * Map an HTTP status tone → background+text class pair for the status pill.
 * Uses opacity-derived surfaces so every theme preset renders correctly
 * even when `--{status}-background` is undefined.
 */
export const STATUS_TONE_PILL: Record<HttpStatusTone, string> = {
  success: 'bg-success/15 text-success',
  info: 'bg-info/15 text-info',
  warning: 'bg-warning/15 text-warning',
  destructive: 'bg-destructive/15 text-destructive',
  muted: 'bg-muted text-muted-foreground',
};

/**
 * Map an HTTP method tone → text-only class. Method label has no background.
 */
export const METHOD_TONE_TEXT: Record<HttpMethodTone, string> = {
  success: 'text-success',
  info: 'text-info',
  warning: 'text-warning',
  destructive: 'text-destructive',
  muted: 'text-muted-foreground',
};
