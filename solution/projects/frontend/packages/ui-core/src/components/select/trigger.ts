import { cn } from '../../lib/utils';
import { CONTROL_SIZE } from '../forms/control-size';

/**
 * The shared class list for a select-like trigger.
 *
 * Every picker in this folder renders its closed state as a `Button` — that is
 * what gives it the focus ring, the border and the disabled handling for free.
 * But a button is an ACTION, and `Button` styles it accordingly with
 * `font-semibold`; a picker's closed state is a FIELD showing a value, and a
 * value has no business being heavier than the label above it. Left alone the
 * trigger rendered "Volkswagen" bolder than its own "Make" label, and the
 * placeholder came out bold too.
 *
 * `font-normal` restores the weight `Input` uses — the control it actually
 * belongs next to in a form. It sits here rather than in seven component files
 * so the next picker inherits the decision instead of re-deciding it.
 */
export const SELECT_TRIGGER_CLASS = "w-full justify-between font-normal";

/**
 * The same, for pickers whose trigger grows with its content (chips, tags,
 * multiple rows) instead of keeping a fixed control height.
 */
export const SELECT_TRIGGER_MULTI_CLASS = cn(
  "w-full justify-between font-normal h-auto py-2",
  CONTROL_SIZE.default.minHeight,
);
