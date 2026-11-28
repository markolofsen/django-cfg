/**
 * Native-engine date/time fields.
 *
 * A typeable, token-skinned field family built on the browser's native
 * `<input type="date|time|datetime-local">` engine, with an optional
 * calendar/columns popover for pointer users. See
 * `@dev/planned/ui-core-datetime-fields/PLAN.md` for the rationale.
 *
 * @module datetime-field
 */

export { DateField } from './date-field';
export type { DateFieldProps } from './date-field';

export { TimeField } from './time-field';
export type { TimeFieldProps } from './time-field';

export { DateTimeField } from './date-time-field';
export type { DateTimeFieldProps } from './date-time-field';

// Low-level building blocks, exported for advanced composition.
export { NativeFieldShell, NATIVE_FIELD_INPUT_CLASS } from './native-field-shell';
export type { NativeFieldShellProps } from './native-field-shell';
export {
  parseDateString,
  formatDateString,
  parseDateTimeString,
  splitDateTime,
  joinDateTime,
} from './date-time-utils';
