"use client"

import * as React from 'react';

import * as SliderPrimitive from '@radix-ui/react-slider';

import { useStoredValue, type StorageType, type UseStoredValueOptions } from '../../../hooks';
import { cn } from '../../../lib/utils';

export interface SliderProps extends React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root> {
  /**
   * When provided, the slider value is persisted under this key.
   * Works with both controlled (`value`) and uncontrolled (`defaultValue`) modes.
   * @example storageKey="volume-level"
   */
  storageKey?: string
  /** @default 'local' */
  storageType?: StorageType
  /** TTL in ms */
  storageTtl?: number
  /**
   * Rendered inside the track, behind the filled range.
   *
   * For a second quantity that shares the track's scale — a media player's
   * buffered extent is the case this exists for. Positioned by the caller and
   * never interactive: the slider owns every pointer event on the track.
   */
  trackDecoration?: React.ReactNode
  /**
   * Extra classes for the track, the filled range and the thumb.
   *
   * These parts live inside this component, so a consumer cannot reach them:
   * a descendant selector would have to name classes it does not own, and
   * arbitrary Tailwind variants targeting them are not reliably generated.
   * A media scrubber needs a hairline track and a thumb that only appears on
   * hover, which is what these exist for.
   */
  trackClassName?: string
  rangeClassName?: string
  thumbClassName?: string
}

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(({ className, orientation = 'horizontal', storageKey, storageType, storageTtl, trackDecoration, trackClassName, rangeClassName, thumbClassName, onValueChange, ...props }, ref) => {
  const isVertical = orientation === 'vertical';

  const storageOptions: UseStoredValueOptions | undefined =
    storageKey ? { storage: storageType ?? 'local', ttl: storageTtl } : undefined;

  const [storedValue, setStoredValue] = useStoredValue<number[]>(
    storageKey,
    (props.defaultValue as number[] | undefined) ?? (props.value as number[] | undefined) ?? [],
    storageOptions,
  );

  const handleValueChange = React.useCallback(
    (newValue: number[]) => {
      if (storageKey) setStoredValue(newValue);
      onValueChange?.(newValue);
    },
    [storageKey, setStoredValue, onValueChange],
  );

  const sliderProps = {
    ...props,
    onValueChange: storageKey ? handleValueChange : onValueChange,
    // Inject stored defaultValue only in uncontrolled mode
    ...(storageKey && props.value === undefined && storedValue.length > 0
      ? { defaultValue: storedValue }
      : {}),
  };

  return (
    <SliderPrimitive.Root
      ref={ref}
      data-slot="slider"
      orientation={orientation}
      className={cn(
        "relative flex touch-none select-none",
        isVertical
          ? "flex-col items-center"
          : "flex-row items-center w-full",
        className
      )}
      {...sliderProps}
    >
      <SliderPrimitive.Track
        data-slot="slider-track"
        className={cn(
          "relative overflow-hidden rounded-full bg-primary/20",
          isVertical ? "w-1.5 h-full grow" : "h-1.5 w-full grow",
          trackClassName
        )}
      >
        {/* Renders BEHIND the range, inside the track, so a consumer that has a
            secondary quantity to show (a media player's buffered extent) does not
            have to fork this component or overlay a second element. */}
        {trackDecoration}
        <SliderPrimitive.Range
          data-slot="slider-range"
          className={cn(
            "absolute bg-primary",
            isVertical ? "w-full bottom-0" : "h-full left-0",
            rangeClassName
          )}
        />
      </SliderPrimitive.Track>
      {/* The accessible name and value text belong on the THUMB: that is where
          Radix puts `role="slider"`, so a label left on the Root names a
          generic element and the control itself stays anonymous. */}
      <SliderPrimitive.Thumb
        data-slot="slider-thumb"
        aria-label={props['aria-label']}
        aria-labelledby={props['aria-labelledby']}
        aria-valuetext={props['aria-valuetext']}
        className={cn(
          "block h-4 w-4 rounded-full border border-primary/50 bg-background shadow transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
          thumbClassName
        )}
      />
    </SliderPrimitive.Root>
  );
})
Slider.displayName = SliderPrimitive.Root.displayName

export { Slider }
