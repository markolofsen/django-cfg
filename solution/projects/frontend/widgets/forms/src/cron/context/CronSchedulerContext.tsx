'use client';

/**
 * CronScheduler Context
 *
 * Provides centralized state management for the CronScheduler component.
 * All child components subscribe to this context for state and actions.
 */

import {
  createContext,
  useContext,
  useMemo,
  useCallback,
  useState,
  useEffect,
  useRef,
} from 'react';
import type {
  CronSchedulerContextValue,
  CronSchedulerState,
  CronSchedulerProviderProps,
  ScheduleType,
  WeekDay,
  MonthDay,
} from '../types';
import { buildCron } from '../utils/cron-builder';
import { parseCron } from '../utils/cron-parser';
import { humanizeCron } from '../utils/cron-humanize';

// ============================================================================
// Context
// ============================================================================

const CronSchedulerContext = createContext<CronSchedulerContextValue | null>(null);

// ============================================================================
// Default State
// ============================================================================

const DEFAULT_STATE: CronSchedulerState = {
  type: 'daily',
  hour: 9,
  minute: 0,
  weekDays: [1, 2, 3, 4, 5] as WeekDay[], // Mon-Fri
  monthDays: [1] as MonthDay[],
  customCron: '* * * * *',
  isValid: true,
};

// ============================================================================
// Provider
// ============================================================================

export function CronSchedulerProvider({
  children,
  value,
  onChange,
  defaultType = 'daily',
  size = 'default',
}: CronSchedulerProviderProps) {
  // Track if this is initial mount to avoid calling onChange on mount
  const isInitialMount = useRef(true);

  // Store onChange in a ref to avoid triggering effects when it changes
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  // Track initial value from props (for showing "original" vs "current")
  const [initialValue] = useState(() => value || null);

  // Initialize state from value prop or defaults
  const [state, setState] = useState<CronSchedulerState>(() => {
    try {
      if (value) {
        const parsed = parseCron(value);
        if (parsed) return parsed;
      }
    } catch {
      // Fallback to default on any parsing error
    }
    return { ...DEFAULT_STATE, type: defaultType };
  });

  // Sync with external value (controlled component support)
  useEffect(() => {
    try {
      if (value) {
        const parsed = parseCron(value);
        if (parsed) {
          const currentCron = buildCron(state);
          if (value !== currentCron) {
            setState(parsed);
          }
        }
      }
    } catch {
      // Ignore parsing errors, keep current state
    }
  }, [value]); // eslint-disable-line react-hooks/exhaustive-deps

  // Computed: cron expression
  const cronExpression = useMemo(() => buildCron(state), [state]);

  // Computed: human-readable description
  const humanDescription = useMemo(() => humanizeCron(cronExpression), [cronExpression]);

  // Notify parent on change (skip initial mount)
  // Use ref to avoid re-triggering when onChange identity changes
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    onChangeRef.current?.(cronExpression);
  }, [cronExpression]);

  // ============================================================================
  // Actions
  // ============================================================================

  const setType = useCallback((type: ScheduleType) => {
    setState(s => ({ ...s, type }));
  }, []);

  const setTime = useCallback((hour: number, minute: number) => {
    setState(s => ({
      ...s,
      hour: Math.max(0, Math.min(23, hour)),
      minute: Math.max(0, Math.min(59, minute)),
    }));
  }, []);

  const toggleWeekDay = useCallback((day: WeekDay) => {
    setState(s => {
      const hasDay = s.weekDays.includes(day);
      // Prevent deselecting the last day
      if (hasDay && s.weekDays.length === 1) return s;

      const newDays = hasDay
        ? s.weekDays.filter(d => d !== day)
        : [...s.weekDays, day];

      return {
        ...s,
        weekDays: newDays.sort((a, b) => a - b) as WeekDay[],
      };
    });
  }, []);

  const setWeekDays = useCallback((days: WeekDay[]) => {
    setState(s => ({
      ...s,
      weekDays: days.length > 0
        ? [...days].sort((a, b) => a - b) as WeekDay[]
        : [1] as WeekDay[], // Default to Monday if empty
    }));
  }, []);

  const toggleMonthDay = useCallback((day: MonthDay) => {
    setState(s => {
      const hasDay = s.monthDays.includes(day);
      // Prevent deselecting the last day
      if (hasDay && s.monthDays.length === 1) return s;

      const newDays = hasDay
        ? s.monthDays.filter(d => d !== day)
        : [...s.monthDays, day];

      return {
        ...s,
        monthDays: newDays.sort((a, b) => a - b) as MonthDay[],
      };
    });
  }, []);

  const setMonthDays = useCallback((days: MonthDay[]) => {
    setState(s => ({
      ...s,
      monthDays: days.length > 0
        ? [...days].sort((a, b) => a - b) as MonthDay[]
        : [1] as MonthDay[], // Default to 1st if empty
    }));
  }, []);

  const setCustomCron = useCallback((customCron: string) => {
    const parsed = parseCron(customCron);
    setState(s => ({
      ...s,
      customCron,
      isValid: parsed !== null,
    }));
  }, []);

  const reset = useCallback(() => {
    setState({ ...DEFAULT_STATE, type: defaultType });
  }, [defaultType]);

  // ============================================================================
  // Context Value
  // ============================================================================

  const contextValue: CronSchedulerContextValue = useMemo(
    () => ({
      // State
      ...state,
      // Config
      size,
      // Computed
      cronExpression,
      humanDescription,
      initialValue,
      // Actions
      setType,
      setTime,
      toggleWeekDay,
      setWeekDays,
      toggleMonthDay,
      setMonthDays,
      setCustomCron,
      reset,
    }),
    [
      state,
      size,
      cronExpression,
      humanDescription,
      initialValue,
      setType,
      setTime,
      toggleWeekDay,
      setWeekDays,
      toggleMonthDay,
      setMonthDays,
      setCustomCron,
      reset,
    ]
  );

  return (
    <CronSchedulerContext.Provider value={contextValue}>
      {children}
    </CronSchedulerContext.Provider>
  );
}

// ============================================================================
// Context Hook
// ============================================================================

export function useCronSchedulerContext(): CronSchedulerContextValue {
  const context = useContext(CronSchedulerContext);
  if (!context) {
    throw new Error(
      'useCronSchedulerContext must be used within CronSchedulerProvider'
    );
  }
  return context;
}
