"use client"

import { X } from "lucide-react";
import * as React from "react";

import { cn } from "../../../lib/utils";

// =============================================================================
// Types
// =============================================================================

export type TagValue = string;

export interface TagsInputRootProps
  extends Omit<
    React.ComponentPropsWithoutRef<"div">,
    "value" | "defaultValue" | "onChange" | "children"
  > {
  /** Controlled array of tag values. */
  value?: TagValue[];
  /** Initial array of tag values when uncontrolled. */
  defaultValue?: TagValue[];
  /** Callback when tag values change. */
  onChange?: (value: TagValue[]) => void;
  /** Validate a tag before adding. Return false to reject. */
  onValidate?: (value: TagValue) => boolean;
  /** Callback when a tag is rejected (duplicate or invalid). */
  onTagInvalid?: (value: TagValue) => void;
  /** Function to convert a tag value to its display string. */
  displayValue?: (value: TagValue) => string;
  /** Add tags on paste (split by delimiter). @default false */
  addOnPaste?: boolean;
  /** Add tags on Tab key. @default false */
  addOnTab?: boolean;
  /** Disable the entire input. @default false */
  disabled?: boolean;
  /** Allow editing existing tags. @default false */
  editable?: boolean;
  /** Wrap focus from last to first. @default false */
  loop?: boolean;
  /** Behavior on blur: "add" | "clear" | undefined. @default undefined */
  blurBehavior?: "add" | "clear";
  /** Delimiter for paste splitting. @default "," */
  delimiter?: string;
  /** Max number of tags. @default Infinity */
  max?: number;
  /** Read-only. @default false */
  readOnly?: boolean;
  /** Required in form. @default false */
  required?: boolean;
  /** Form field name. */
  name?: string;
  /** Unique id. */
  id?: string;
  /** Children or render prop. */
  children?: React.ReactNode | ((context: { value: TagValue[] }) => React.ReactNode);
}

export type TagsInputInputProps = Omit<React.ComponentPropsWithoutRef<"input">, "value" | "defaultValue">;

export interface TagsInputItemProps extends React.ComponentPropsWithoutRef<"div"> {
  /** The value of the item. */
  value: TagValue;
  /** Whether the item is disabled. */
  disabled?: boolean;
}

export type TagsInputItemTextProps = React.ComponentPropsWithoutRef<"span">;

export type TagsInputItemDeleteProps = React.ComponentPropsWithoutRef<"button">;

// =============================================================================
// Context
// =============================================================================

interface TagsInputContextValue {
  value: TagValue[];
  onValueChange: (value: TagValue[]) => void;
  onItemAdd: (textValue: string, options?: { viaPaste?: boolean }) => boolean;
  onItemRemove: (index: number) => void;
  onItemUpdate: (index: number, newTextValue: string) => void;
  onInputKeydown: (event: React.KeyboardEvent) => void;
  highlightedIndex: number | null;
  setHighlightedIndex: (index: number | null) => void;
  editingIndex: number | null;
  setEditingIndex: (index: number | null) => void;
  displayValue: (value: TagValue) => string;
  onItemLeave: () => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
  addOnPaste: boolean;
  addOnTab: boolean;
  delimiter: string;
  disabled: boolean;
  editable: boolean;
  isInvalidInput: boolean;
  loop: boolean;
  readOnly: boolean;
  blurBehavior: "add" | "clear" | undefined;
  max: number;
  id: string;
  inputId: string;
  labelId: string;
}

const TagsInputContext = React.createContext<TagsInputContextValue | null>(null);

function useTagsInput(componentName: string) {
  const context = React.useContext(TagsInputContext);
  if (!context) {
    throw new Error(`${componentName} must be used within <TagsInput>`);
  }
  return context;
}

interface TagsInputItemContextValue {
  id: string;
  value: TagValue;
  index: number;
  isHighlighted: boolean;
  isEditing: boolean;
  disabled?: boolean;
  textId: string;
  displayValue: string;
}

const TagsInputItemContext = React.createContext<TagsInputItemContextValue | null>(null);

function useTagsInputItem(componentName: string) {
  const context = React.useContext(TagsInputItemContext);
  if (!context) {
    throw new Error(`${componentName} must be used within <TagsInputItem>`);
  }
  return context;
}

// =============================================================================
// Root
// =============================================================================

const DATA_ITEM_ATTR = "data-tags-input-item";

const TagsInput = React.forwardRef<HTMLDivElement, TagsInputRootProps>(
  (props, ref) => {
    const {
      value: valueProp,
      defaultValue,
      onChange,
      onValidate,
      onTagInvalid,
      displayValue = (value: TagValue) => value.toString(),
      addOnPaste = false,
      addOnTab = false,
      disabled = false,
      editable = false,
      loop = false,
      blurBehavior,
      delimiter = ",",
      max = Number.POSITIVE_INFINITY,
      readOnly = false,
      required = false,
      name,
      children,
      id: idProp,
      className,
      ...rootProps
    } = props;

    const [value = [], setValue] = React.useState<TagValue[] | undefined>(defaultValue);
    /*
     * Memoised because the `?? []` branch mints a NEW array each render, and
     * four `useCallback`s below take `resolvedValue` as a dependency — so an
     * uncontrolled, empty TagsInput rebuilt all four on every render and the
     * memoisation bought nothing. Identity is what those hooks compare.
     */
    const resolvedValue = React.useMemo(
      () => (valueProp !== undefined ? valueProp : (value ?? [])),
      [valueProp, value],
    );

    const [highlightedIndex, setHighlightedIndex] = React.useState<number | null>(null);
    const [editingIndex, setEditingIndex] = React.useState<number | null>(null);
    const [isInvalidInput, setIsInvalidInput] = React.useState(false);
    const collectionRef = React.useRef<HTMLDivElement>(null);
    const inputRef = React.useRef<HTMLInputElement>(null);

    // useId must be called unconditionally — `idProp ?? React.useId()` skips the
    // hook whenever a caller passes `id`, so the hook count differs between
    // renders/instances and React crashes (#310). Call it, then prefer idProp.
    const generatedId = React.useId();
    const id = idProp ?? generatedId;
    const inputId = React.useId();
    const labelId = React.useId();

    const isFormControl = React.useRef(false);
    React.useEffect(() => {
      if (collectionRef.current) {
        isFormControl.current = !!collectionRef.current.closest("form");
      }
    }, []);

    const getEnabledItems = React.useCallback(() => {
      if (!collectionRef.current) return [];
      return Array.from(collectionRef.current.querySelectorAll(`[${DATA_ITEM_ATTR}]`));
    }, []);

    const onItemAdd = React.useCallback(
      (textValue: string, options?: { viaPaste?: boolean }) => {
        if (disabled || readOnly) return false;

        if (addOnPaste && options?.viaPaste) {
          const splitValues = textValue
            .split(delimiter)
            .map((v) => v.trim())
            .filter(Boolean);

          if (resolvedValue.length + splitValues.length > max && max > 0) {
            onTagInvalid?.(textValue);
            return false;
          }

          const newValues = [...new Set(splitValues.filter((v) => !resolvedValue.includes(v)))];
          const validValues = newValues.filter((v) => !onValidate || onValidate(v));

          if (validValues.length === 0) return false;

          const nextValue = [...resolvedValue, ...validValues];
          if (valueProp === undefined) setValue(nextValue);
          onChange?.(nextValue);
          return true;
        }

        if (resolvedValue.length >= max && max > 0) {
          onTagInvalid?.(textValue);
          return false;
        }

        const trimmedValue = textValue.trim();
        if (onValidate && !onValidate(trimmedValue)) {
          setIsInvalidInput(true);
          onTagInvalid?.(trimmedValue);
          return false;
        }

        const exists = resolvedValue.some((v) => v === trimmedValue);
        if (exists) {
          setIsInvalidInput(true);
          onTagInvalid?.(trimmedValue);
          return true;
        }

        const nextValue = [...resolvedValue, trimmedValue];
        if (valueProp === undefined) setValue(nextValue);
        onChange?.(nextValue);
        setHighlightedIndex(null);
        setEditingIndex(null);
        setIsInvalidInput(false);
        return true;
      },
      [resolvedValue, max, addOnPaste, delimiter, onChange, onTagInvalid, onValidate, disabled, readOnly, valueProp]
    );

    const onItemUpdate = React.useCallback(
      (index: number, newTextValue: string) => {
        if (disabled || readOnly) return;
        if (index === -1) return;

        const trimmedValue = newTextValue.trim();
        const exists = resolvedValue.some((v, i) => i !== index && v === trimmedValue);
        if (exists) {
          setIsInvalidInput(true);
          onTagInvalid?.(trimmedValue);
          return;
        }

        if (onValidate && !onValidate(trimmedValue)) {
          setIsInvalidInput(true);
          onTagInvalid?.(trimmedValue);
          return;
        }

        const nextValue = [...resolvedValue];
        nextValue[index] = displayValue(trimmedValue);
        if (valueProp === undefined) setValue(nextValue);
        onChange?.(nextValue);
        setHighlightedIndex(index);
        setEditingIndex(null);
        setIsInvalidInput(false);

        requestAnimationFrame(() => inputRef.current?.focus());
      },
      [resolvedValue, onChange, displayValue, onTagInvalid, onValidate, disabled, readOnly, valueProp]
    );

    const onItemRemove = React.useCallback(
      (index: number) => {
        if (disabled || readOnly) return;
        if (index === -1) return;

        const nextValue = [...resolvedValue];
        nextValue.splice(index, 1);
        if (valueProp === undefined) setValue(nextValue);
        onChange?.(nextValue);
        setHighlightedIndex(null);
        setEditingIndex(null);
        inputRef.current?.focus();
      },
      [resolvedValue, onChange, disabled, readOnly, valueProp]
    );

    const onItemLeave = React.useCallback(() => {
      setHighlightedIndex(null);
      setEditingIndex(null);
      inputRef.current?.focus();
    }, []);

    const findNextEnabledIndex = React.useCallback(
      (currentIndex: number | null, direction: "next" | "prev"): number | null => {
        const enabledItems = getEnabledItems();
        const enabledIndices = enabledItems.map((_, index) => index);
        if (enabledIndices.length === 0) return null;

        if (currentIndex === null) {
          return direction === "prev"
            ? (enabledIndices[enabledIndices.length - 1] ?? null)
            : (enabledIndices[0] ?? null);
        }

        const currentEnabledIndex = enabledIndices.indexOf(currentIndex);
        if (direction === "next") {
          return currentEnabledIndex >= enabledIndices.length - 1
            ? loop
              ? (enabledIndices[0] ?? null)
              : null
            : (enabledIndices[currentEnabledIndex + 1] ?? null);
        }

        return currentEnabledIndex <= 0
          ? loop
            ? (enabledIndices[enabledIndices.length - 1] ?? null)
            : null
          : (enabledIndices[currentEnabledIndex - 1] ?? null);
      },
      [getEnabledItems, loop]
    );

    const onInputKeydown = React.useCallback(
      (event: React.KeyboardEvent) => {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) return;

        const isArrowLeft = event.key === "ArrowLeft";
        const isArrowRight = event.key === "ArrowRight";

        if (target.value && target.selectionStart !== 0) {
          setHighlightedIndex(null);
          setEditingIndex(null);
          return;
        }

        switch (event.key) {
          case "Delete":
          case "Backspace": {
            if (target.selectionStart !== 0 || target.selectionEnd !== 0) break;
            if (highlightedIndex !== null) {
              const newIndex = findNextEnabledIndex(highlightedIndex, "prev");
              onItemRemove(highlightedIndex);
              setHighlightedIndex(newIndex);
              event.preventDefault();
            } else if (event.key === "Backspace" && resolvedValue.length > 0) {
              const lastIndex = findNextEnabledIndex(null, "prev");
              setHighlightedIndex(lastIndex);
              event.preventDefault();
            }
            break;
          }
          case "Enter": {
            if (highlightedIndex !== null && editable && !disabled) {
              setEditingIndex(highlightedIndex);
              event.preventDefault();
            }
            break;
          }
          case "ArrowLeft":
          case "ArrowRight": {
            if (target.selectionStart === 0 && isArrowLeft && highlightedIndex === null && resolvedValue.length > 0) {
              const lastIndex = findNextEnabledIndex(null, "prev");
              setHighlightedIndex(lastIndex);
              event.preventDefault();
            } else if (highlightedIndex !== null) {
              const nextIndex = findNextEnabledIndex(highlightedIndex, isArrowLeft ? "prev" : "next");
              if (nextIndex !== null) {
                setHighlightedIndex(nextIndex);
                event.preventDefault();
              } else if (isArrowRight) {
                setHighlightedIndex(null);
                requestAnimationFrame(() => target.setSelectionRange(0, 0));
              }
            }
            break;
          }
          case "Home": {
            if (highlightedIndex !== null) {
              const firstIndex = findNextEnabledIndex(null, "next");
              setHighlightedIndex(firstIndex);
              event.preventDefault();
            }
            break;
          }
          case "End": {
            if (highlightedIndex !== null) {
              const lastIndex = findNextEnabledIndex(null, "prev");
              setHighlightedIndex(lastIndex);
              event.preventDefault();
            }
            break;
          }
          case "Escape": {
            if (highlightedIndex !== null) setHighlightedIndex(null);
            if (editingIndex !== null) setEditingIndex(null);
            requestAnimationFrame(() => target.setSelectionRange(0, 0));
            break;
          }
        }
      },
      [resolvedValue, highlightedIndex, editingIndex, onItemRemove, findNextEnabledIndex, editable, disabled]
    );

    const getIsClickedInEmptyRoot = React.useCallback(
      (target: HTMLElement) => {
        return (
          collectionRef.current?.contains(target) &&
          !target.hasAttribute(DATA_ITEM_ATTR) &&
          target.tagName !== "INPUT"
        );
      },
      []
    );

    return (
      <TagsInputContext.Provider
        value={{
          value: resolvedValue,
          onValueChange: onChange ?? (() => {}),
          onItemAdd,
          onItemRemove,
          onItemUpdate,
          onInputKeydown,
          highlightedIndex,
          setHighlightedIndex,
          editingIndex,
          setEditingIndex,
          displayValue,
          onItemLeave,
          inputRef,
          isInvalidInput,
          addOnPaste,
          addOnTab,
          disabled,
          editable,
          loop,
          readOnly,
          blurBehavior,
          delimiter,
          max,
          id,
          inputId,
          labelId,
        }}
      >
        <div
          id={id}
          ref={(node) => {
            collectionRef.current = node;
            if (typeof ref === "function") {
              ref(node);
            } else if (ref) {
              (ref as React.MutableRefObject<HTMLDivElement | null>).current = node;
            }
          }}
          data-disabled={disabled ? "" : undefined}
          data-invalid={isInvalidInput ? "" : undefined}
          data-readonly={readOnly ? "" : undefined}
          className={cn(
            "flex flex-wrap items-center gap-1.5 rounded-[var(--radius)] border border-border bg-transparent px-2 py-1.5 text-sm shadow-sm transition-colors",
            "focus-within:ring-1 focus-within:ring-ring",
            disabled && "cursor-not-allowed opacity-50",
            className
          )}
          onClick={(event) => {
            rootProps.onClick?.(event);
            const target = event.target;
            if (!(target instanceof HTMLElement)) return;
            if (
              getIsClickedInEmptyRoot(target) &&
              document.activeElement !== inputRef.current
            ) {
              event.currentTarget.focus();
              inputRef.current?.focus();
            }
          }}
          onMouseDown={(event) => {
            rootProps.onMouseDown?.(event);
            const target = event.target;
            if (!(target instanceof HTMLElement)) return;
            if (getIsClickedInEmptyRoot(target)) {
              event.preventDefault();
            }
          }}
          onBlur={(event) => {
            rootProps.onBlur?.(event);
            if (
              event.relatedTarget !== inputRef.current &&
              !collectionRef.current?.contains(event.relatedTarget as Node)
            ) {
              requestAnimationFrame(() => setHighlightedIndex(null));
            }
          }}
          {...rootProps}
        >
          {typeof children === "function" ? children({ value: resolvedValue }) : children}
          {isFormControl.current && name && (
            <input type="hidden" name={name} value={resolvedValue.join(delimiter)} disabled={disabled} required={required} />
          )}
        </div>
      </TagsInputContext.Provider>
    );
  }
);

TagsInput.displayName = "TagsInput";

// =============================================================================
// Input
// =============================================================================

const TagsInputInput = React.forwardRef<HTMLInputElement, TagsInputInputProps>(
  (props, ref) => {
    const { autoFocus, ...inputProps } = props;
    const context = useTagsInput("TagsInputInput");
    const { onItemAdd, setHighlightedIndex, addOnTab, inputRef } = context;

    const onCustomKeydown = React.useCallback(
      (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.defaultPrevented) return;
        const value = event.currentTarget.value;
        if (!value) return;
        const isAdded = onItemAdd(value);
        if (isAdded) {
          event.currentTarget.value = "";
          setHighlightedIndex(null);
        }
        event.preventDefault();
      },
      [onItemAdd, setHighlightedIndex]
    );

    const onTab = React.useCallback(
      (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (!addOnTab) return;
        onCustomKeydown(event);
      },
      [addOnTab, onCustomKeydown]
    );

    React.useEffect(() => {
      if (!autoFocus) return;
      const id = requestAnimationFrame(() => inputRef.current?.focus());
      return () => cancelAnimationFrame(id);
    }, [autoFocus, inputRef]);

    const composedRef = React.useCallback(
      (node: HTMLInputElement | null) => {
        inputRef.current = node;
        if (typeof ref === "function") {
          ref(node);
        } else if (ref) {
          (ref as React.MutableRefObject<HTMLInputElement | null>).current = node;
        }
      },
      [ref, inputRef]
    );

    return (
      <input
        type="text"
        id={context.inputId}
        autoCapitalize="off"
        autoComplete="off"
        autoCorrect="off"
        spellCheck="false"
        autoFocus={autoFocus}
        aria-labelledby={context.labelId}
        aria-readonly={context.readOnly}
        data-invalid={context.isInvalidInput ? "" : undefined}
        disabled={context.disabled}
        readOnly={context.readOnly}
        {...inputProps}
        ref={composedRef}
        className={cn(
          "flex-1 bg-transparent outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 min-w-[60px]",
          inputProps.className
        )}
        onBlur={(event) => {
          inputProps.onBlur?.(event);
          if (context.readOnly) return;
          if (context.blurBehavior === "add") {
            const val = event.target.value;
            if (val) {
              const isAdded = context.onItemAdd(val);
              if (isAdded) event.target.value = "";
            }
          }
          if (context.blurBehavior === "clear") {
            event.target.value = "";
          }
        }}
        onChange={(event) => {
          inputProps.onChange?.(event);
          if (context.readOnly) return;
          const target = event.target;
          if (!(target instanceof HTMLInputElement)) return;
          const delimiter = context.delimiter;
          if (delimiter === target.value.slice(-1)) {
            const val = target.value.slice(0, -1);
            target.value = "";
            if (val) {
              context.onItemAdd(val);
              context.setHighlightedIndex(null);
            }
          }
        }}
        onKeyDown={(event) => {
          inputProps.onKeyDown?.(event);
          if (context.readOnly) return;
          if (event.key === "Enter") onCustomKeydown(event);
          if (event.key === "Tab") onTab(event);
          context.onInputKeydown(event);
          if (event.key.length === 1) context.setHighlightedIndex(null);
        }}
        onPaste={(event) => {
          inputProps.onPaste?.(event);
          if (context.readOnly) return;
          if (context.addOnPaste) {
            event.preventDefault();
            const val = event.clipboardData.getData("text");
            context.onItemAdd(val, { viaPaste: true });
            context.setHighlightedIndex(null);
          }
        }}
      />
    );
  }
);

TagsInputInput.displayName = "TagsInputInput";

// =============================================================================
// Item
// =============================================================================

const TagsInputItem = React.forwardRef<HTMLDivElement, TagsInputItemProps>(
  (props, ref) => {
    const { value, disabled: itemDisabledProp, ...itemProps } = props;
    const pointerTypeRef = React.useRef<React.PointerEvent["pointerType"]>("touch");
    const context = useTagsInput("TagsInputItem");
    const id = React.useId();
    const textId = `${id}text`;
    const index = context.value.indexOf(value);
    const isHighlighted = index === context.highlightedIndex;
    const isEditing = index === context.editingIndex;
    const itemDisabled = itemDisabledProp || context.disabled;
    const displayValue = context.displayValue(value);

    const { setHighlightedIndex, inputRef } = context;
    const onItemSelect = React.useCallback(() => {
      setHighlightedIndex(index);
      inputRef.current?.focus();
    }, [setHighlightedIndex, inputRef, index]);

    return (
      <TagsInputItemContext.Provider
        value={{
          id,
          value,
          index,
          isHighlighted,
          isEditing,
          disabled: itemDisabled,
          textId,
          displayValue,
        }}
      >
        <div
          id={id}
          ref={ref}
          aria-labelledby={textId}
          aria-current={isHighlighted}
          aria-disabled={itemDisabled}
          {...{ [DATA_ITEM_ATTR]: "" }}
          data-state={isHighlighted ? "active" : "inactive"}
          data-highlighted={isHighlighted ? "" : undefined}
          data-editing={isEditing ? "" : undefined}
          data-editable={context.editable ? "" : undefined}
          data-disabled={itemDisabled ? "" : undefined}
          {...itemProps}
          // Spread stays ABOVE className and the handlers: below them, a consumer
          // that passes any of these props replaces the composed behaviour
          // outright — a tag with an onClick stops being selectable.
          className={cn(
            "inline-flex items-center gap-1 rounded-[var(--radius)] border bg-secondary px-2 py-0.5 text-sm text-secondary-foreground transition-colors",
            isHighlighted && "ring-1 ring-ring",
            itemDisabled && "opacity-50 cursor-not-allowed",
            itemProps.className
          )}
          onClick={(event) => {
            itemProps.onClick?.(event);
            event.stopPropagation();
            if (!isEditing && pointerTypeRef.current !== "mouse") {
              onItemSelect();
            }
          }}
          onDoubleClick={(event) => {
            itemProps.onDoubleClick?.(event);
            if (context.editable && !itemDisabled) {
              requestAnimationFrame(() => context.setEditingIndex(index));
            }
          }}
          onPointerUp={(event) => {
            itemProps.onPointerUp?.(event);
            if (pointerTypeRef.current === "mouse") onItemSelect();
          }}
          onPointerDown={(event) => {
            itemProps.onPointerDown?.(event);
            pointerTypeRef.current = event.pointerType;
          }}
          onPointerMove={(event) => {
            itemProps.onPointerMove?.(event);
            pointerTypeRef.current = event.pointerType;
            if (itemDisabledProp) {
              context.onItemLeave();
            } else if (pointerTypeRef.current === "mouse") {
              event.currentTarget.focus({ preventScroll: true });
            }
          }}
          onPointerLeave={(event) => {
            itemProps.onPointerLeave?.(event);
            if (event.currentTarget === document.activeElement) {
              context.onItemLeave();
            }
          }}
        />
      </TagsInputItemContext.Provider>
    );
  }
);

TagsInputItem.displayName = "TagsInputItem";

// =============================================================================
// ItemText
// =============================================================================

function TagsInputEditableItemText() {
  const context = useTagsInput("TagsInputEditableItemText");
  const itemContext = useTagsInputItem("TagsInputEditableItemText");
  const [editValue, setEditValue] = React.useState(itemContext.displayValue);

  const { setEditingIndex, setHighlightedIndex, onItemUpdate, inputRef, value: contextValue } = context;
  const { displayValue, value: itemValue, index: itemIndex } = itemContext;

  const onBlur = React.useCallback(() => {
    setEditValue(displayValue);
    setEditingIndex(null);
  }, [setEditingIndex, displayValue]);

  const onChange = React.useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const target = event.target;
    target.style.width = "0";
    target.style.width = `${target.scrollWidth + 4}px`;
    setEditValue(event.target.value);
  }, []);

  const onFocus = React.useCallback((event: React.FocusEvent<HTMLInputElement>) => {
    event.target.select();
    event.target.style.width = "0";
    event.target.style.width = `${event.target.scrollWidth + 4}px`;
  }, []);

  const onKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key === "Enter") {
        const index = contextValue.indexOf(itemValue);
        onItemUpdate(index, editValue);
      } else if (event.key === "Escape") {
        setEditValue(displayValue);
        setEditingIndex(null);
        setHighlightedIndex(itemIndex);
        inputRef.current?.focus();
      }
      event.stopPropagation();
    },
    [
      contextValue,
      onItemUpdate,
      setEditingIndex,
      displayValue,
      editValue,
      itemValue,
      setHighlightedIndex,
      itemIndex,
      inputRef,
    ]
  );

  return (
    <input
      type="text"
      autoCapitalize="off"
      autoComplete="off"
      autoCorrect="off"
      spellCheck="false"
      autoFocus
      aria-describedby={itemContext.textId}
      value={editValue}
      onChange={onChange}
      onKeyDown={onKeyDown}
      onFocus={onFocus}
      onBlur={onBlur}
      className="bg-transparent outline-none min-w-[1ch]"
      style={{
        font: "inherit",
        color: "inherit",
        padding: 0,
        border: "none",
      }}
    />
  );
}

const TagsInputItemText = React.forwardRef<HTMLSpanElement, TagsInputItemTextProps>(
  (props, ref) => {
    const { children, ...itemTextProps } = props;
    const context = useTagsInput("TagsInputItemText");
    const itemContext = useTagsInputItem("TagsInputItemText");

    if (itemContext.isEditing && context.editable && !itemContext.disabled) {
      return <TagsInputEditableItemText />;
    }

    return (
      <span id={itemContext.textId} {...itemTextProps} ref={ref}>
        {children ?? itemContext.displayValue}
      </span>
    );
  }
);

TagsInputItemText.displayName = "TagsInputItemText";

// =============================================================================
// ItemDelete
// =============================================================================

const TagsInputItemDelete = React.forwardRef<HTMLButtonElement, TagsInputItemDeleteProps>(
  (props, ref) => {
    const context = useTagsInput("TagsInputItemDelete");
    const itemContext = useTagsInputItem("TagsInputItemDelete");
    const disabled = itemContext.disabled || context.disabled;

    if (itemContext.isEditing) return null;

    return (
      <button
        type="button"
        ref={ref}
        tabIndex={disabled ? undefined : -1}
        aria-labelledby={itemContext.textId}
        aria-controls={itemContext.id}
        aria-current={itemContext.isHighlighted}
        data-state={itemContext.isHighlighted ? "active" : "inactive"}
        data-disabled={disabled ? "" : undefined}
        className={cn(
          "inline-flex items-center justify-center rounded-sm opacity-70 transition-opacity hover:opacity-100 focus:outline-none focus:ring-1 focus:ring-ring",
          disabled && "pointer-events-none opacity-50",
          props.className
        )}
        onClick={(event) => {
          props.onClick?.(event);
          if (disabled) return;
          const index = context.value.indexOf(itemContext.value);
          context.onItemRemove(index);
        }}
        {...props}
      >
        {props.children ?? <X className="h-3 w-3" />}
      </button>
    );
  }
);

TagsInputItemDelete.displayName = "TagsInputItemDelete";

// =============================================================================
// Exports
// =============================================================================

export {
  TagsInput,
  TagsInputInput,
  TagsInputItem,
  TagsInputItemText,
  TagsInputItemDelete,
};

