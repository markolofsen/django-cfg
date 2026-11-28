/**
 * Logger
 *
 * Universal logger with consola + zustand store integration.
 * Logs are accumulated for Console panel display.
 * In production, only logs to store (no console output).
 */

'use client';

import { consola } from 'consola';

import { useLogStore } from './logStore';

import type { Logger, LogLevel, MediaLogger } from './types';

import { isDev, isBrowser } from '../env';

// Create base consola instance
const baseConsola = consola.create({
  level: isDev ? 4 : 2, // 4 = debug, 2 = warn
});

/**
 * Extract error details from unknown error type
 */
function extractErrorData(data?: Record<string, unknown>): {
  cleanData: Record<string, unknown> | undefined;
  stack: string | undefined;
} {
  if (!data) return { cleanData: undefined, stack: undefined };

  const cleanData = { ...data };
  let stack: string | undefined;

  // Extract stack from error object
  if (data.error instanceof Error) {
    stack = data.error.stack;
    cleanData.error = {
      name: data.error.name,
      message: data.error.message,
    };
  } else if (typeof data.error === 'object' && data.error !== null) {
    const errObj = data.error as Record<string, unknown>;
    if (typeof errObj.stack === 'string') {
      stack = errObj.stack;
    }
    if (typeof errObj.message === 'string') {
      cleanData.error = errObj.message;
    }
  }

  return { cleanData, stack };
}

/**
 * Format buffer ranges for logging
 */
function formatBufferRanges(buffered: TimeRanges, duration: number): string {
  if (buffered.length === 0) return 'empty';

  const ranges: string[] = [];
  for (let i = 0; i < buffered.length; i++) {
    const start = buffered.start(i);
    const end = buffered.end(i);
    const percent = ((end - start) / duration * 100).toFixed(1);
    ranges.push(`${start.toFixed(1)}-${end.toFixed(1)}s (${percent}%)`);
  }
  return ranges.join(', ');
}

/**
 * Create a logger for a specific component/module
 */
export function createLogger(component: string): Logger {
  const consolaTagged = baseConsola.withTag(component);

  const log = (level: LogLevel, message: string, data?: Record<string, unknown>) => {
    const { cleanData, stack } = extractErrorData(data);

    // Add to store (for Console panel)
    if (isBrowser) {
      useLogStore.getState().addLog({
        level,
        component,
        message,
        data: cleanData,
        stack,
      });
    }

    // Log to console via consola (in dev mode)
    if (isDev) {
      const consolaMethod = level === 'success' ? 'success' : level;
      if (cleanData) {
        consolaTagged[consolaMethod](message, cleanData);
      } else {
        consolaTagged[consolaMethod](message);
      }
    }
  };

  return {
    debug: (message, data) => log('debug', message, data),
    info: (message, data) => log('info', message, data),
    warn: (message, data) => log('warn', message, data),
    error: (message, data) => log('error', message, data),
    success: (message, data) => log('success', message, data),
  };
}

/**
 * Create a media-specific logger with helper methods
 * for AudioPlayer, VideoPlayer, ImageViewer
 */
export function createMediaLogger(component: string): MediaLogger {
  const baseLogger = createLogger(component);

  return {
    ...baseLogger,

    load: (src: string, type?: string) => {
      const typeStr = type ? ` (${type})` : '';
      baseLogger.info(`LOAD: ${src}${typeStr}`);
    },

    state: (state: string, details?: Record<string, unknown>) => {
      baseLogger.debug(`STATE: ${state}`, details);
    },

    seek: (from: number, to: number, duration: number) => {
      baseLogger.debug(`SEEK: ${from.toFixed(2)}s -> ${to.toFixed(2)}s`, {
        from,
        to,
        duration,
        progress: `${((to / duration) * 100).toFixed(1)}%`,
      });
    },

    buffer: (buffered: TimeRanges, duration: number) => {
      if (buffered.length > 0) {
        baseLogger.debug(`BUFFER: ${formatBufferRanges(buffered, duration)}`);
      }
    },

    event: (name: string, data?: unknown) => {
      if (data !== undefined) {
        baseLogger.debug(`EVENT: ${name}`, { data });
      } else {
        baseLogger.debug(`EVENT: ${name}`);
      }
    },
  };
}

/**
 * Global logger for non-component code
 */
export const logger = createLogger('App');

/**
 * Quick access for one-off logs
 */
export const log = {
  debug: (component: string, message: string, data?: Record<string, unknown>) =>
    createLogger(component).debug(message, data),
  info: (component: string, message: string, data?: Record<string, unknown>) =>
    createLogger(component).info(message, data),
  warn: (component: string, message: string, data?: Record<string, unknown>) =>
    createLogger(component).warn(message, data),
  error: (component: string, message: string, data?: Record<string, unknown>) =>
    createLogger(component).error(message, data),
  success: (component: string, message: string, data?: Record<string, unknown>) =>
    createLogger(component).success(message, data),
};
