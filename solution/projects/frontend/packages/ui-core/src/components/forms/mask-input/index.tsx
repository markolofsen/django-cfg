"use client"

import * as React from "react";

import { cn } from "../../../lib/utils";
import { CONTROL_SIZE } from "../control-size";

// =============================================================================
// Types
// =============================================================================

export type MaskToken =
  | "0" // digit
  | "a" // letter
  | "*" // alphanumeric
  | string; // literal

export interface MaskDefinition {
  /** Character that represents this token in the mask pattern */
  token: MaskToken;
  /** Regex to validate the character at this position */
  pattern: RegExp;
  /** Whether this token is optional */
  optional?: boolean;
  /** Transform function for the character */
  transform?: (char: string) => string;
}

export interface MaskInputProps extends Omit<React.ComponentProps<"input">, "value" | "defaultValue" | "onChange" | "onBeforeInput"> {
  onBeforeInput?: (event: React.FormEvent<HTMLInputElement> & { data?: string }) => void;
  /** Mask pattern, e.g. "(000) 000-0000" or "00/00/0000" */
  mask: string;
  /** Custom mask definitions. Defaults to digit-only. */
  definitions?: Record<string, MaskDefinition>;
  /** Controlled value (raw, unmasked) */
  value?: string;
  /** Default uncontrolled value (raw, unmasked) */
  defaultValue?: string;
  /** Callback when raw value changes */
  onChange?: (value: string) => void;
  /** Character used for empty mask positions */
  maskChar?: string;
  /** Whether to always show the mask */
  alwaysShowMask?: boolean;
  /** Whether to clean the value on blur if incomplete */
  cleanOnBlur?: boolean;
}

// =============================================================================
// Default Definitions
// =============================================================================

const defaultDefinitions: Record<string, MaskDefinition> = {
  "0": { token: "0", pattern: /\d/ },
  "a": { token: "a", pattern: /[a-zA-Z]/, transform: (c) => c.toLowerCase() },
  "A": { token: "A", pattern: /[a-zA-Z]/, transform: (c) => c.toUpperCase() },
  "*": { token: "*", pattern: /[a-zA-Z0-9]/ },
};

// =============================================================================
// Utilities
// =============================================================================

function parseMask(
  mask: string,
  definitions: Record<string, MaskDefinition>
): Array<{ type: "literal"; char: string } | { type: "token"; def: MaskDefinition }> {
  const result: ReturnType<typeof parseMask> = [];
  for (const char of mask) {
    const def = definitions[char];
    if (def) {
      result.push({ type: "token", def });
    } else {
      result.push({ type: "literal", char });
    }
  }
  return result;
}

function applyMask(
  rawValue: string,
  maskParts: ReturnType<typeof parseMask>,
  maskChar: string
): { masked: string; raw: string; complete: boolean } {
  let rawIndex = 0;
  let masked = "";
  let raw = "";
  let complete = true;

  for (const part of maskParts) {
    if (part.type === "literal") {
      masked += part.char;
      continue;
    }

    if (rawIndex < rawValue.length) {
      const char = rawValue[rawIndex];
      if (char === undefined) {
        masked += maskChar;
        complete = false;
        continue;
      }
      if (part.def.pattern.test(char)) {
        const transformed = part.def.transform ? part.def.transform(char) : char;
        masked += transformed;
        raw += transformed;
        rawIndex++;
      } else {
        // Invalid char for this position — skip it
        rawIndex++;
        // Re-process this mask position with next raw char
        const nextChar = rawValue[rawIndex];
        if (nextChar && part.def.pattern.test(nextChar)) {
          const transformed = part.def.transform ? part.def.transform(nextChar) : nextChar;
          masked += transformed;
          raw += transformed;
          rawIndex++;
        } else {
          masked += maskChar;
          complete = false;
        }
      }
    } else {
      masked += maskChar;
      complete = false;
    }
  }

  return { masked, raw, complete };
}

function extractRaw(value: string, maskParts: ReturnType<typeof parseMask>): string {
  let raw = "";
  let valueIndex = 0;
  for (const part of maskParts) {
    if (valueIndex >= value.length) break;
    const char = value[valueIndex];
    if (char === undefined) break;
    if (part.type === "literal") {
      if (char === part.char) {
        valueIndex++;
      }
      continue;
    }
    if (part.def.pattern.test(char)) {
      raw += part.def.transform ? part.def.transform(char) : char;
    }
    valueIndex++;
  }
  return raw;
}

function getNextTokenIndex(
  maskParts: ReturnType<typeof parseMask>,
  currentIndex: number,
  direction: 1 | -1
): number {
  let index = currentIndex + direction;
  while (index >= 0 && index < maskParts.length) {
    if (maskParts[index]?.type === "token") return index;
    index += direction;
  }
  return direction === 1 ? maskParts.length : -1;
}

// =============================================================================
// Component
// =============================================================================

const MaskInput = React.forwardRef<HTMLInputElement, MaskInputProps>(
  (
    {
      mask,
      definitions = defaultDefinitions,
      value: controlledValue,
      defaultValue = "",
      onChange,
      maskChar = "_",
      alwaysShowMask = false,
      cleanOnBlur = false,
      className,
      onFocus,
      onBlur,
      onKeyDown,
      onBeforeInput,
      ...props
    },
    ref
  ) => {
    const maskParts = React.useMemo(() => parseMask(mask, definitions), [mask, definitions]);
    const isControlled = controlledValue !== undefined;

    const [internalRaw, setInternalRaw] = React.useState(defaultValue);
    const rawValue = isControlled ? controlledValue : internalRaw;

    const { masked: maskedValue } = React.useMemo(
      () => applyMask(rawValue, maskParts, maskChar),
      [rawValue, maskParts, maskChar]
    );

    const inputRef = React.useRef<HTMLInputElement>(null);
    const composedRef = React.useMemo(() => {
      return (node: HTMLInputElement | null) => {
        inputRef.current = node;
        if (typeof ref === "function") {
          ref(node);
        } else if (ref) {
          (ref as React.MutableRefObject<HTMLInputElement | null>).current = node;
        }
      };
    }, [ref]);

    const [isFocused, setIsFocused] = React.useState(false);
    const displayValue = alwaysShowMask || isFocused ? maskedValue : rawValue || "";

    // Controlled inputs reset caret to end on every value commit, so all
    // caret moves (focus + every keystroke that rewrites the value) defer
    // through this ref and run from useLayoutEffect after the render.
    const pendingCaretRef = React.useRef<number | null>(null);

    const updateValue = React.useCallback(
      (newRaw: string) => {
        if (!isControlled) {
          setInternalRaw(newRaw);
        }
        onChange?.(newRaw);
      },
      [isControlled, onChange]
    );

    const handleBeforeInput = React.useCallback(
      (event: React.FormEvent<HTMLInputElement> & { data?: string }) => {
        onBeforeInput?.(event);
        if (event.defaultPrevented) return;

        const input = event.currentTarget;
        const data = event.data;
        if (!data) return;

        const start = input.selectionStart ?? 0;
        // NOTE: only the selection START is consulted. A non-collapsed
        // selection (`selectionEnd !== start`) is validated as if the caret sat
        // at its left edge, so typing over a selection checks the wrong mask
        // slot. handleKeyDown below does handle `start !== end`; this path does
        // not. Left as-is — fixing it changes input behaviour.

        // Determine which mask position we're at
        let maskPos = 0;
        let charCount = 0;
        for (let i = 0; i < maskParts.length && charCount < start; i++) {
          if (maskParts[i]?.type === "token") {
            charCount++;
          }
          maskPos = i + 1;
        }

        // Find next token position
        const nextToken = getNextTokenIndex(maskParts, maskPos - 1, 1);
        if (nextToken === -1 || nextToken >= maskParts.length) {
          event.preventDefault();
          return;
        }

        const part = maskParts[nextToken];
        if (!part || part.type !== "token") {
          event.preventDefault();
          return;
        }

        if (!part.def.pattern.test(data)) {
          event.preventDefault();
          return;
        }
      },
      [maskParts, onBeforeInput]
    );

    const handleKeyDown = React.useCallback(
      (event: React.KeyboardEvent<HTMLInputElement>) => {
        onKeyDown?.(event);
        if (event.defaultPrevented) return;

        const input = event.currentTarget;
        const start = input.selectionStart ?? 0;
        const end = input.selectionEnd ?? 0;

        if (event.key === "Backspace") {
          event.preventDefault();
          if (start !== end) {
            const before = input.value.slice(0, start);
            const after = input.value.slice(end);
            const newRaw = extractRaw(before + after, maskParts);
            let pos = start;
            while (pos > 0 && maskParts[pos - 1]?.type === "literal") pos--;
            pendingCaretRef.current = pos;
            updateValue(newRaw);
            return;
          }

          if (start === 0) return;

          let pos = start - 1;
          while (pos >= 0 && maskParts[pos]?.type === "literal") pos--;
          if (pos < 0) return;

          const currentRaw = extractRaw(input.value, maskParts);
          let rawIndex = 0;
          for (let i = 0; i < pos; i++) {
            if (maskParts[i]?.type === "token") rawIndex++;
          }

          const newRaw = currentRaw.slice(0, rawIndex) + currentRaw.slice(rawIndex + 1);
          pendingCaretRef.current = pos;
          updateValue(newRaw);
          return;
        }

        if (event.key === "Delete") {
          event.preventDefault();
          if (start !== end) {
            const before = input.value.slice(0, start);
            const after = input.value.slice(end);
            const newRaw = extractRaw(before + after, maskParts);
            pendingCaretRef.current = start;
            updateValue(newRaw);
            return;
          }

          const currentRaw = extractRaw(input.value, maskParts);
          let rawIndex = 0;
          for (let i = 0; i < start; i++) {
            if (maskParts[i]?.type === "token") rawIndex++;
          }

          if (rawIndex >= currentRaw.length) return;

          const newRaw = currentRaw.slice(0, rawIndex) + currentRaw.slice(rawIndex + 1);
          pendingCaretRef.current = start;
          updateValue(newRaw);
          return;
        }

        if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
          // Let default happen but skip over literals
          requestAnimationFrame(() => {
            const newStart = input.selectionStart ?? 0;
            const direction = event.key === "ArrowLeft" ? -1 : 1;
            let pos = newStart;
            if (direction === -1) {
              pos--;
              while (pos >= 0 && maskParts[pos]?.type === "literal") pos--;
              if (pos >= 0) {
                input.setSelectionRange(pos + 1, pos + 1);
              }
            } else {
              while (pos < maskParts.length && maskParts[pos]?.type === "literal") pos++;
              input.setSelectionRange(pos, pos);
            }
          });
          return;
        }

        if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
          event.preventDefault();
          const char = event.key;

          const nextToken = getNextTokenIndex(maskParts, start - 1, 1);
          if (nextToken === -1 || nextToken >= maskParts.length) return;

          const part = maskParts[nextToken];
          if (!part || part.type !== "token") return;
          if (!part.def.pattern.test(char)) return;

          const currentRaw = extractRaw(input.value, maskParts);
          let rawIndex = 0;
          for (let i = 0; i < nextToken; i++) {
            if (maskParts[i]?.type === "token") rawIndex++;
          }

          const transformed = part.def.transform ? part.def.transform(char) : char;
          const newRaw = currentRaw.slice(0, rawIndex) + transformed + currentRaw.slice(rawIndex + 1);

          let nextPos = nextToken + 1;
          while (nextPos < maskParts.length && maskParts[nextPos]?.type === "literal") nextPos++;
          pendingCaretRef.current = nextPos;

          updateValue(newRaw);
        }
      },
      [maskParts, onKeyDown, updateValue]
    );

    const computeNextEmptyCaret = React.useCallback(() => {
      const filledCount = rawValue.length;
      let tokenSeen = 0;
      for (let i = 0; i < maskParts.length; i++) {
        if (maskParts[i]?.type === "token") {
          if (tokenSeen === filledCount) return i;
          tokenSeen++;
        }
      }
      return maskParts.length;
    }, [maskParts, rawValue]);

    const handleFocus = React.useCallback(
      (event: React.FocusEvent<HTMLInputElement>) => {
        setIsFocused(true);
        onFocus?.(event);
        // setIsFocused triggers re-render to masked display. The caret
        // must be placed AFTER that render committed, otherwise the
        // browser defaults to end-of-string. useLayoutEffect below does
        // the placement; we just record where to go.
        pendingCaretRef.current = computeNextEmptyCaret();
      },
      [onFocus, computeNextEmptyCaret]
    );

    React.useLayoutEffect(() => {
      if (pendingCaretRef.current == null) return;
      const input = inputRef.current;
      if (!input) return;
      const pos = pendingCaretRef.current;
      pendingCaretRef.current = null;
      input.setSelectionRange(pos, pos);
    });

    const handleBlur = React.useCallback(
      (event: React.FocusEvent<HTMLInputElement>) => {
        setIsFocused(false);
        onBlur?.(event);
        if (cleanOnBlur) {
          const { complete } = applyMask(rawValue, maskParts, maskChar);
          if (!complete) {
            updateValue("");
          }
        }
      },
      [cleanOnBlur, rawValue, maskParts, maskChar, onBlur, updateValue]
    );

    const handleChange = React.useCallback(
      (event: React.ChangeEvent<HTMLInputElement>) => {
        // Extract raw from whatever the user managed to input
        const newRaw = extractRaw(event.target.value, maskParts);
        updateValue(newRaw);
      },
      [maskParts, updateValue]
    );

    return (
      <input
        type="text"
        inputMode="numeric"
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck="false"
        {...props}
        ref={composedRef}
        value={displayValue}
        className={cn(
          CONTROL_SIZE.default.height,
          "flex w-full rounded-[var(--radius)] border border-border bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          className
        )}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        onBeforeInput={handleBeforeInput}
      />
    );
  }
);

MaskInput.displayName = "MaskInput";

export { MaskInput };
