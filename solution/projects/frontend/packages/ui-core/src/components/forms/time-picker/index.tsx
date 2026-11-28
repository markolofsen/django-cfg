"use client"

import { Clock } from "lucide-react";
import * as React from "react";

import { useComposedRefs } from "../../../lib/compose-refs";
import { cn } from "../../../lib/utils";
import { Button } from "../../forms/button";
import { Popover, PopoverContent, PopoverTrigger } from "../../overlay/popover";

// =============================================================================
// Types
// =============================================================================

export interface TimePickerProps {
  /** Selected time value as HH:mm string */
  value?: string;
  /** Default uncontrolled value */
  defaultValue?: string;
  /** Callback when time changes (HH:mm) */
  onChange?: (value: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Disable the picker */
  disabled?: boolean;
  /** Use 12-hour format with AM/PM */
  use12Hour?: boolean;
  /** Minimum time (HH:mm) */
  min?: string;
  /** Maximum time (HH:mm) */
  max?: string;
  /** Step in minutes for minute selector @default 1 */
  minuteStep?: number;
  /** Additional class for trigger button */
  className?: string;
  /** Button variant */
  variant?: "default" | "outline" | "ghost";
  /** Align popover */
  align?: "start" | "center" | "end";
  /** Form field name */
  name?: string;
}

// =============================================================================
// Utilities
// =============================================================================

function parseTime(timeStr: string): { hours: number; minutes: number } | null {
  const match = timeStr.match(/^(\d{1,2}):(\d{2})$/);
  if (!match) return null;
  const hoursPart = match[1];
  const minutesPart = match[2];
  if (hoursPart === undefined || minutesPart === undefined) return null;
  const hours = parseInt(hoursPart, 10);
  const minutes = parseInt(minutesPart, 10);
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) return null;
  return { hours, minutes };
}

function formatTime(hours: number, minutes: number): string {
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

function format12Hour(hours: number, minutes: number): string {
  const period = hours >= 12 ? "PM" : "AM";
  const h = hours % 12 || 12;
  return `${String(h).padStart(2, "0")}:${String(minutes).padStart(2, "0")} ${period}`;
}

function isTimeInRange(time: string, min?: string, max?: string): boolean {
  if (min && time < min) return false;
  if (max && time > max) return false;
  return true;
}

// =============================================================================
// Component
// =============================================================================

const TimePicker = React.forwardRef<HTMLButtonElement, TimePickerProps>(
  (
    {
      value: controlledValue,
      defaultValue,
      onChange,
      placeholder = "Select time",
      disabled = false,
      use12Hour = false,
      min,
      max,
      minuteStep = 1,
      className,
      variant = "outline",
      align = "start",
      name,
    },
    ref
  ) => {
    const isControlled = controlledValue !== undefined;
    const [internalValue, setInternalValue] = React.useState(defaultValue ?? "");
    const resolvedValue = isControlled ? controlledValue : internalValue;

    const [open, setOpen] = React.useState(false);
    const [tempHours, setTempHours] = React.useState(0);
    const [tempMinutes, setTempMinutes] = React.useState(0);
    const [tempPeriod, setTempPeriod] = React.useState<"AM" | "PM">("AM");

    const parsed = React.useMemo(() => parseTime(resolvedValue), [resolvedValue]);

    // Sync temp values when opening popover
    React.useEffect(() => {
      if (open && parsed) {
        setTempHours(parsed.hours);
        setTempMinutes(parsed.minutes);
        setTempPeriod(parsed.hours >= 12 ? "PM" : "AM");
      } else if (open) {
        setTempHours(12);
        setTempMinutes(0);
        setTempPeriod("AM");
      }
    }, [open, parsed]);

    const updateValue = React.useCallback(
      (hours: number, minutes: number) => {
        const formatted = formatTime(hours, minutes);
        if (!isControlled) {
          setInternalValue(formatted);
        }
        onChange?.(formatted);
      },
      [isControlled, onChange]
    );

    const handleApply = React.useCallback(() => {
      let hours = tempHours;
      if (use12Hour) {
        if (tempPeriod === "PM" && hours !== 12) hours += 12;
        if (tempPeriod === "AM" && hours === 12) hours = 0;
      }
      const formatted = formatTime(hours, tempMinutes);
      if (isTimeInRange(formatted, min, max)) {
        updateValue(hours, tempMinutes);
        setOpen(false);
      }
    }, [tempHours, tempMinutes, tempPeriod, use12Hour, min, max, updateValue]);

    const displayValue = React.useMemo(() => {
      if (!parsed) return placeholder;
      if (use12Hour) {
        return format12Hour(parsed.hours, parsed.minutes);
      }
      return formatTime(parsed.hours, parsed.minutes);
    }, [parsed, use12Hour, placeholder]);

    // Generate hour options
    const hourOptions = React.useMemo(() => {
      if (use12Hour) {
        return Array.from({ length: 12 }, (_, i) => i + 1);
      }
      return Array.from({ length: 24 }, (_, i) => i);
    }, [use12Hour]);

    // Generate minute options
    const minuteOptions = React.useMemo(() => {
      const steps = Math.floor(60 / minuteStep);
      return Array.from({ length: steps }, (_, i) => i * minuteStep);
    }, [minuteStep]);

    const isFormControl = React.useRef(false);
    // The trigger is a <button>, and the caller's ref must see `null` before it
    // mounts. useImperativeHandle cannot express that — it must produce a
    // handle — so the two refs are composed onto the element instead.
    const rootRef = React.useRef<HTMLButtonElement | null>(null);
    const composedRef = useComposedRefs(rootRef, ref);

    React.useEffect(() => {
      if (rootRef.current) {
        isFormControl.current = !!rootRef.current.closest("form");
      }
    }, []);

    return (
      <>
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              ref={composedRef}
              variant={variant}
              disabled={disabled}
              className={cn(
                "w-full justify-start text-left font-normal",
                !resolvedValue && "text-muted-foreground",
                className
              )}
            >
              <Clock className="mr-2 h-4 w-4" />
              {displayValue}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-3" align={align}>
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2">
                {/* Hours */}
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-muted-foreground text-center">Hour</span>
                  <div className="flex flex-col max-h-48 overflow-y-auto border rounded-[var(--radius)]">
                    {hourOptions.map((h) => {
                      const selected = use12Hour
                        ? (tempHours % 12 || 12) === h
                        : tempHours === h;
                      return (
                        <button
                          key={h}
                          type="button"
                          onClick={() => setTempHours(use12Hour ? h : h)}
                          className={cn(
                            "px-3 py-1.5 text-sm text-left hover:bg-accent transition-colors",
                            selected && "bg-primary text-primary-foreground hover:bg-primary/90"
                          )}
                        >
                          {String(h).padStart(2, "0")}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <span className="text-lg font-medium text-muted-foreground">:</span>

                {/* Minutes */}
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-muted-foreground text-center">Min</span>
                  <div className="flex flex-col max-h-48 overflow-y-auto border rounded-[var(--radius)]">
                    {minuteOptions.map((m) => {
                      const selected = tempMinutes === m;
                      return (
                        <button
                          key={m}
                          type="button"
                          onClick={() => setTempMinutes(m)}
                          className={cn(
                            "px-3 py-1.5 text-sm text-left hover:bg-accent transition-colors",
                            selected && "bg-primary text-primary-foreground hover:bg-primary/90"
                          )}
                        >
                          {String(m).padStart(2, "0")}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* AM/PM */}
                {use12Hour && (
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-muted-foreground text-center">&nbsp;</span>
                    <div className="flex flex-col border rounded-[var(--radius)]">
                      {(["AM", "PM"] as const).map((p) => (
                        <button
                          key={p}
                          type="button"
                          onClick={() => setTempPeriod(p)}
                          className={cn(
                            "px-3 py-1.5 text-sm text-left hover:bg-accent transition-colors",
                            tempPeriod === p && "bg-primary text-primary-foreground hover:bg-primary/90"
                          )}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Button size="sm" onClick={handleApply} className="w-full">
                Apply
              </Button>
            </div>
          </PopoverContent>
        </Popover>
        {isFormControl.current && name && (
          <input type="hidden" name={name} value={resolvedValue} disabled={disabled} />
        )}
      </>
    );
  }
);

TimePicker.displayName = "TimePicker";

export { TimePicker };
