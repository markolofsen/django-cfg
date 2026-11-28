"use client"

import * as React from 'react';

import { cn } from '../../../lib/utils';
import type { FieldControlSize } from '../control-size';
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from '../input-group';

/**
 * An input with a fixed symbol before and/or after the value.
 *
 * `InputGroup` already does this, but it takes four components and the right
 * `align` on each — enough ceremony that a currency field gets written as a
 * bare `Input` with the unit in the label instead, which is how a form ends up
 * not saying what unit it is in.
 *
 * This is the same thing in one component:
 *
 *   <InputAffix prefix="$" value={price} onChange={onPrice} />
 *   <InputAffix suffix="%" value={rate} onChange={onRate} />
 *   <InputAffix prefix="$" suffix="/ yr" value={rent} onChange={onRent} />
 *
 * The affixes are **static marks, not content**: a currency symbol, a unit, a
 * per-period suffix. They carry `aria-hidden` because the accessible name
 * belongs on the field's label — a screen reader announcing "dollar sign" as
 * it enters the field is noise, and a label reading "Purchase price in US
 * dollars" is the thing that actually helps. Where an affix carries meaning
 * the label does not, put it in the label or in a `FieldDescription`.
 *
 * Not for a button, a select, or anything interactive. Reach for `InputGroup`
 * directly there — that is what `InputGroupButton` is for.
 */
export interface InputAffixProps
  extends Omit<React.ComponentProps<typeof InputGroupInput>, 'prefix'> {
  /** Shown before the value — a currency symbol, a unit. */
  prefix?: React.ReactNode;
  /** Shown after the value — a unit, a period. */
  suffix?: React.ReactNode;
  /** Applied to the group, so callers can size the whole control. */
  groupClassName?: string;
  /** Height from the shared control ladder — same names as `Input`'s `inputSize`. */
  inputSize?: FieldControlSize;
}

const InputAffix = React.forwardRef<HTMLInputElement, InputAffixProps>(
  ({ prefix, suffix, className, groupClassName, inputSize, ...props }, ref) => (
    <InputGroup className={groupClassName} inputSize={inputSize}>
      {prefix ? (
        <InputGroupAddon align="inline-start" aria-hidden="true">
          {prefix}
        </InputGroupAddon>
      ) : null}
      <InputGroupInput ref={ref} className={cn(className)} {...props} />
      {suffix ? (
        <InputGroupAddon align="inline-end" aria-hidden="true">
          {suffix}
        </InputGroupAddon>
      ) : null}
    </InputGroup>
  ),
);
InputAffix.displayName = 'InputAffix';

export { InputAffix };
