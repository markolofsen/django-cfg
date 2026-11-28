/**
 * CronScheduler Types
 *
 * Unix 5-field cron format: minute hour day-of-month month day-of-week
 */

// ============================================================================
// Base Types
// ============================================================================

export type ScheduleType = 'daily' | 'weekly' | 'monthly' | 'custom';

/**
 * Visual density of the scheduler fields.
 * - `default` — full-size fields (unchanged).
 * - `sm` — compact fields for narrow side panels / modals (~360-420px).
 */
export type CronSchedulerSize = 'default' | 'sm';

/** Day of week: 0 = Sunday, 1 = Monday, ..., 6 = Saturday */
export type WeekDay = 0 | 1 | 2 | 3 | 4 | 5 | 6;

/** Day of month: 1-31 */
export type MonthDay =
  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10
  | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20
  | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31;

// ============================================================================
// State Types
// ============================================================================

export interface CronSchedulerState {
  /** Current schedule type */
  type: ScheduleType;
  /** Hour (0-23) */
  hour: number;
  /** Minute (0-59) */
  minute: number;
  /** Selected week days (for weekly type) */
  weekDays: WeekDay[];
  /** Selected month days (for monthly type) */
  monthDays: MonthDay[];
  /** Raw cron expression (for custom type) */
  customCron: string;
  /** Whether current state produces valid cron */
  isValid: boolean;
}

export interface CronSchedulerComputed {
  /** Generated cron expression */
  cronExpression: string;
  /** Human-readable description */
  humanDescription: string;
  /** Initial value from props (null if not provided) */
  initialValue: string | null;
}

// ============================================================================
// Action Types
// ============================================================================

export interface CronSchedulerActions {
  /** Set schedule type */
  setType: (type: ScheduleType) => void;
  /** Set time (hour and minute) */
  setTime: (hour: number, minute: number) => void;
  /** Toggle a week day selection */
  toggleWeekDay: (day: WeekDay) => void;
  /** Set all week days at once */
  setWeekDays: (days: WeekDay[]) => void;
  /** Toggle a month day selection */
  toggleMonthDay: (day: MonthDay) => void;
  /** Set all month days at once */
  setMonthDays: (days: MonthDay[]) => void;
  /** Set custom cron expression */
  setCustomCron: (cron: string) => void;
  /** Reset to default state */
  reset: () => void;
}

// ============================================================================
// Context Types
// ============================================================================

export interface CronSchedulerContextValue
  extends CronSchedulerState,
    CronSchedulerComputed,
    CronSchedulerActions {
  /** Visual density of the fields (`default` | `sm`) */
  size: CronSchedulerSize;
}

// ============================================================================
// Component Props
// ============================================================================

export interface CronSchedulerProps {
  /** Current cron expression (Unix 5-field format) */
  value?: string;
  /** Callback when schedule changes */
  onChange?: (cron: string) => void;
  /** Initial schedule type (default: 'daily') */
  defaultType?: ScheduleType;
  /** Show raw cron expression below the trigger (default: false) */
  showCronExpression?: boolean;
  /** Allow copying cron expression (default: false) */
  allowCopy?: boolean;
  /** 12h or 24h time format (default: '24h') */
  timeFormat?: '12h' | '24h';
  /** Disable all interactions */
  disabled?: boolean;
  /**
   * Render the schedule editor expanded instead of behind a popover
   * trigger (legacy layout). Default: false — compact popover surface.
   */
  inline?: boolean;
  /** Trigger text shown when no schedule is set (compact mode only) */
  placeholder?: string;
  /**
   * Visual density of the fields. `sm` renders smaller, tighter fields
   * suited for narrow side panels / modals. Default: `default`.
   */
  size?: CronSchedulerSize;
  /** Additional CSS classes */
  className?: string;
}

export interface CronSchedulerProviderProps {
  children: React.ReactNode;
  value?: string;
  onChange?: (cron: string) => void;
  defaultType?: ScheduleType;
  /** Visual density propagated to all field components. Default: `default`. */
  size?: CronSchedulerSize;
}
