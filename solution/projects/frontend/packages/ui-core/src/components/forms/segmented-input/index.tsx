"use client"

import * as React from "react";

import { cn } from "../../../lib/utils";

// =============================================================================
// Types
// =============================================================================

export interface SegmentedInputProps extends Omit<React.ComponentProps<"input">, "value" | "defaultValue" | "onChange" | "size" | "pattern"> {
  /** Number of segments */
  length?: number;
  /** Controlled value */
  value?: string;
  /** Default uncontrolled value */
  defaultValue?: string;
  /** Callback when value changes */
  onChange?: (value: string) => void;
  /** Callback when all segments are filled */
  onComplete?: (value: string) => void;
  /** Visual separator between segments */
  separator?: React.ReactNode;
  /** Position(s) where separator appears (after these 0-based indices) */
  separatorIndices?: number[];
  /** Whether to auto-focus first segment on mount */
  autoFocus?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Custom class for each segment */
  segmentClassName?: string;
  /** Custom class for the container */
  containerClassName?: string;
  /** Custom class for separator */
  separatorClassName?: string;
  /** Pattern regex for each character */
  pattern?: RegExp;
  /** Transform input character */
  transform?: (char: string) => string;
  /** Fluid mode — segments stretch to fill container */
  fluid?: boolean;
  /** Size variant */
  size?: "sm" | "default" | "lg";
}

// =============================================================================
// Utilities
// =============================================================================

function cleanValue(value: string, pattern: RegExp, transform?: (char: string) => string): string {
  let cleaned = value.split("").filter((c) => pattern.test(c)).join("");
  if (transform) {
    cleaned = cleaned.split("").map(transform).join("");
  }
  return cleaned;
}

// =============================================================================
// Component
// =============================================================================

const sizeVariants = {
  sm: "h-8 w-8 text-sm",
  default: "h-10 w-10 text-base",
  lg: "h-14 w-14 text-2xl",
};

const SegmentedInput = React.forwardRef<HTMLDivElement, SegmentedInputProps>(
  (
    {
      length = 6,
      value: controlledValue,
      defaultValue = "",
      onChange,
      onComplete,
      separator,
      separatorIndices,
      autoFocus = true,
      disabled = false,
      segmentClassName,
      containerClassName,
      separatorClassName,
      pattern = /[a-zA-Z0-9]/,
      transform,
      fluid = false,
      size = "default",
      name,
      className,
      ...props
    },
    ref
  ) => {
    const isControlled = controlledValue !== undefined;
    const [internalValue, setInternalValue] = React.useState(defaultValue);
    const value = isControlled ? controlledValue : internalValue;

    const inputRefs = React.useRef<(HTMLInputElement | null)[]>([]);
    const [activeIndex, setActiveIndex] = React.useState(-1);

    const cleanedValue = React.useMemo(
      () => cleanValue(value, pattern, transform),
      [value, pattern, transform]
    );

    const updateValue = React.useCallback(
      (newValue: string) => {
        const cleaned = cleanValue(newValue, pattern, transform).slice(0, length);
        if (!isControlled) {
          setInternalValue(cleaned);
        }
        onChange?.(cleaned);
        if (cleaned.length === length) {
          onComplete?.(cleaned);
        }
      },
      [isControlled, onChange, onComplete, length, pattern, transform]
    );

    const focusSegment = React.useCallback((index: number) => {
      if (index >= 0 && index < length) {
        inputRefs.current[index]?.focus();
        inputRefs.current[index]?.select();
      }
    }, [length]);

    const handleSegmentChange = React.useCallback(
      (index: number, inputValue: string) => {
        const char = inputValue.slice(-1);
        if (!pattern.test(char)) return;

        const transformed = transform ? transform(char) : char;
        const newValue = cleanedValue.slice(0, index) + transformed + cleanedValue.slice(index + 1);
        updateValue(newValue);

        if (index < length - 1) {
          focusSegment(index + 1);
        }
      },
      [cleanedValue, updateValue, focusSegment, length, pattern, transform]
    );

    const handleKeyDown = React.useCallback(
      (index: number, event: React.KeyboardEvent<HTMLInputElement>) => {
        switch (event.key) {
          case "ArrowLeft": {
            event.preventDefault();
            if (index > 0) focusSegment(index - 1);
            break;
          }
          case "ArrowRight": {
            event.preventDefault();
            if (index < length - 1) focusSegment(index + 1);
            break;
          }
          case "Backspace": {
            event.preventDefault();
            if (cleanedValue[index]) {
              const newValue = cleanedValue.slice(0, index) + cleanedValue.slice(index + 1);
              updateValue(newValue);
            } else if (index > 0) {
              focusSegment(index - 1);
            }
            break;
          }
          case "Delete": {
            event.preventDefault();
            const newValue = cleanedValue.slice(0, index) + cleanedValue.slice(index + 1);
            updateValue(newValue);
            break;
          }
          case "Home": {
            event.preventDefault();
            focusSegment(0);
            break;
          }
          case "End": {
            event.preventDefault();
            focusSegment(length - 1);
            break;
          }
          default: {
            if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
              if (!pattern.test(event.key)) {
                event.preventDefault();
                return;
              }
              // Let onChange handle the input
            }
          }
        }
      },
      [cleanedValue, focusSegment, length, pattern, updateValue]
    );

    const handlePaste = React.useCallback(
      (event: React.ClipboardEvent<HTMLInputElement>) => {
        event.preventDefault();
        const pasted = event.clipboardData.getData("text");
        const cleaned = cleanValue(pasted, pattern, transform).slice(0, length);
        updateValue(cleaned);

        // Focus the next empty segment or the last one
        const nextEmpty = cleaned.length < length ? cleaned.length : length - 1;
        focusSegment(nextEmpty);
      },
      [length, pattern, transform, updateValue, focusSegment]
    );

    const handleFocus = React.useCallback((index: number) => {
      setActiveIndex(index);
    }, []);

    const handleBlur = React.useCallback(() => {
      setActiveIndex(-1);
    }, []);

    // Auto-focus first segment on mount
    React.useEffect(() => {
      if (autoFocus && !disabled) {
        const timer = setTimeout(() => focusSegment(0), 0);
        return () => clearTimeout(timer);
      }
    }, [autoFocus, disabled, focusSegment]);

    // Determine default separator positions (middle)
    const defaultSeparatorIndices = React.useMemo(() => {
      if (separatorIndices !== undefined) return separatorIndices;
      if (!separator) return [];
      const mid = Math.floor(length / 2);
      return mid > 0 && mid < length ? [mid - 1] : [];
    }, [separatorIndices, separator, length]);

    // Hidden input for form integration
    const isFormControl = React.useRef(false);
    const rootRef = React.useRef<HTMLDivElement>(null);
    React.useImperativeHandle(ref, () => rootRef.current!);

    React.useEffect(() => {
      if (rootRef.current) {
        isFormControl.current = !!rootRef.current.closest("form");
      }
    }, []);

    const slots: React.ReactNode[] = [];
    for (let i = 0; i < length; i++) {
      const char = cleanedValue[i] || "";
      const isActive = activeIndex === i;

      slots.push(
        <input
          key={`segment-${i}`}
          ref={(el) => { inputRefs.current[i] = el; }}
          type="text"
          inputMode="text"
          maxLength={1}
          disabled={disabled}
          value={char}
          data-active={isActive ? "" : undefined}
          data-filled={char ? "" : undefined}
          className={cn(
            "relative flex items-center justify-center border-y border-r border-border text-center text-sm shadow-sm transition-all first:rounded-l-md first:border-l last:rounded-r-md",
            "focus-visible:outline-none focus-visible:z-10 focus-visible:ring-1 focus-visible:ring-ring",
            "disabled:cursor-not-allowed disabled:opacity-50",
            fluid ? `flex-1 min-w-0 aspect-square ${sizeVariants[size]}` : sizeVariants[size],
            segmentClassName
          )}
          onChange={(e) => handleSegmentChange(i, e.target.value)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          onPaste={handlePaste}
          onFocus={() => handleFocus(i)}
          onBlur={handleBlur}
          {...props}
        />
      );

      // Add separator after this index if specified
      if (defaultSeparatorIndices.includes(i) && separator) {
        slots.push(
          <div
            key={`separator-${i}`}
            role="separator"
            className={cn("flex items-center justify-center", separatorClassName)}
          >
            {separator}
          </div>
        );
      }
    }

    return (
      <>
        <div
          ref={rootRef}
          className={cn(
            "flex items-center gap-2 has-[:disabled]:opacity-50",
            fluid && "w-full",
            containerClassName
          )}
        >
          <div className={cn("flex items-center", fluid && "w-full", className)}>
            {slots}
          </div>
        </div>
        {isFormControl.current && name && (
          <input
            type="hidden"
            name={name}
            value={cleanedValue}
            disabled={disabled}
          />
        )}
      </>
    );
  }
);

SegmentedInput.displayName = "SegmentedInput";

export { SegmentedInput };
