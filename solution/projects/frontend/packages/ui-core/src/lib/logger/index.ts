/**
 * Universal Logger
 *
 * Combines console logging with zustand store for Console panel.
 * Use createMediaLogger for media tools (AudioPlayer, VideoPlayer, ImageViewer).
 */

export { createLogger, createMediaLogger, logger, log } from './logger';
export { useLogStore, useFilteredLogs, useLogCount, useErrorCount } from './logStore';
export type { LogEntry, LogLevel, LogFilter, LogStore, Logger, MediaLogger } from './types';
