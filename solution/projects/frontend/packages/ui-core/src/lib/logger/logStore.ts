/**
 * Log Store
 *
 * Zustand store for log accumulation and filtering.
 * Keeps logs in memory for Console panel display.
 */

'use client';

import { create } from 'zustand';

import type { LogStore, LogEntry, LogFilter } from './types';

const DEFAULT_FILTER: LogFilter = {
  levels: ['debug', 'info', 'warn', 'error', 'success'],
  component: undefined,
  search: undefined,
  since: undefined,
};

const MAX_LOGS = 1000;

function generateId(): string {
  return `log-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function matchesFilter(entry: LogEntry, filter: LogFilter): boolean {
  // Level filter
  if (!filter.levels.includes(entry.level)) {
    return false;
  }

  // Component filter (case-insensitive partial match)
  if (filter.component) {
    const comp = filter.component.toLowerCase();
    if (!entry.component.toLowerCase().includes(comp)) {
      return false;
    }
  }

  // Search filter (case-insensitive, searches message and data)
  if (filter.search) {
    const search = filter.search.toLowerCase();
    const inMessage = entry.message.toLowerCase().includes(search);
    const inData = entry.data
      ? JSON.stringify(entry.data).toLowerCase().includes(search)
      : false;
    if (!inMessage && !inData) {
      return false;
    }
  }

  // Time filter
  if (filter.since && entry.timestamp < filter.since) {
    return false;
  }

  return true;
}

export const useLogStore = create<LogStore>((set, get) => ({
  logs: [],
  filter: DEFAULT_FILTER,
  maxLogs: MAX_LOGS,

  addLog: (entry) => {
    const newEntry: LogEntry = {
      ...entry,
      id: generateId(),
      timestamp: new Date(),
    };

    set((state) => {
      const newLogs = [...state.logs, newEntry];
      // Trim to max size
      if (newLogs.length > state.maxLogs) {
        return { logs: newLogs.slice(-state.maxLogs) };
      }
      return { logs: newLogs };
    });
  },

  clearLogs: () => {
    set({ logs: [] });
  },

  setFilter: (filter) => {
    set((state) => ({
      filter: { ...state.filter, ...filter },
    }));
  },

  resetFilter: () => {
    set({ filter: DEFAULT_FILTER });
  },

  getFilteredLogs: () => {
    const { logs, filter } = get();
    return logs.filter((entry) => matchesFilter(entry, filter));
  },

  exportLogs: () => {
    const { logs } = get();
    return JSON.stringify(logs, null, 2);
  },
}));

// Selector hooks for performance
export const useFilteredLogs = () => {
  const logs = useLogStore((state) => state.logs);
  const filter = useLogStore((state) => state.filter);
  return logs.filter((entry) => matchesFilter(entry, filter));
};

export const useLogCount = () => {
  return useLogStore((state) => state.logs.length);
};

export const useErrorCount = () => {
  return useLogStore((state) =>
    state.logs.filter((log) => log.level === 'error').length
  );
};
