"use client"

import * as React from "react";

import { cn } from "../../../lib/utils";
import type { FieldControlSize } from "../control-size";
import { inputClass, TEXTAREA_CLASS } from "../input";

// =============================================================================
// Types
// =============================================================================

export interface EditableRootProps
  extends Omit<React.ComponentPropsWithoutRef<"div">, "value" | "defaultValue" | "onChange" | "onSubmit" | "children"> {
  /** Controlled value */
  value?: string;
  /** Default uncontrolled value */
  defaultValue?: string;
  /** Callback when value changes */
  onValueChange?: (value: string) => void;
  /** Callback when value is submitted (Enter or blur) */
  onValueSubmit?: (value: string) => void;
  /** Callback when editing is cancelled (Escape) */
  onValueCancel?: (previousValue: string) => void;
  /** Whether editing is active (controlled) */
  editing?: boolean;
  /** Callback when editing state changes */
  onEditingChange?: (editing: boolean) => void;
  /** Whether the editable is disabled. @default false */
  disabled?: boolean;
  /** Whether the editable is read-only. @default false */
  readOnly?: boolean;
  /** Whether to select all text on focus. @default true */
  selectAllOnFocus?: boolean;
  /** Whether to submit on blur. @default true */
  submitOnBlur?: boolean;
  /** Placeholder when empty */
  placeholder?: string;
  /** Form field name */
  name?: string;
  /** Children or render prop */
  children?: React.ReactNode;
}

export type EditablePreviewProps = React.ComponentPropsWithoutRef<"span">;

export interface EditableInputProps extends Omit<React.ComponentPropsWithoutRef<"input">, "value" | "defaultValue"> {
  /** Density — matches the standalone Input's `inputSize`. Default: 'default'. */
  inputSize?: FieldControlSize;
}

export type EditableTextareaProps = Omit<React.ComponentPropsWithoutRef<"textarea">, "value" | "defaultValue">;

// =============================================================================
// Context
// =============================================================================

interface EditableContextValue {
  value: string;
  setValue: (value: string) => void;
  isEditing: boolean;
  setIsEditing: (editing: boolean) => void;
  submit: () => void;
  cancel: () => void;
  disabled: boolean;
  readOnly: boolean;
  selectAllOnFocus: boolean;
  submitOnBlur: boolean;
  placeholder?: string;
  inputRef: React.RefObject<HTMLInputElement | null>;
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
  previousValueRef: React.MutableRefObject<string>;
}

const EditableContext = React.createContext<EditableContextValue | null>(null);

function useEditable(componentName: string) {
  const context = React.useContext(EditableContext);
  if (!context) {
    throw new Error(`${componentName} must be used within <Editable>`);
  }
  return context;
}

// =============================================================================
// Root
// =============================================================================

const Editable = React.forwardRef<HTMLDivElement, EditableRootProps>(
  (props, ref) => {
    const {
      value: valueProp,
      defaultValue = "",
      onValueChange,
      onValueSubmit,
      onValueCancel,
      editing: editingProp,
      onEditingChange,
      disabled = false,
      readOnly = false,
      selectAllOnFocus = true,
      submitOnBlur = true,
      placeholder,
      name,
      children,
      className,
      ...rootProps
    } = props;

    const isControlledValue = valueProp !== undefined;
    const isControlledEditing = editingProp !== undefined;

    const [internalValue, setInternalValue] = React.useState(defaultValue);
    const [internalEditing, setInternalEditing] = React.useState(false);

    const resolvedValue = isControlledValue ? valueProp : internalValue;
    const resolvedEditing = isControlledEditing ? editingProp : internalEditing;

    const previousValueRef = React.useRef(resolvedValue);
    const inputRef = React.useRef<HTMLInputElement>(null);
    const textareaRef = React.useRef<HTMLTextAreaElement>(null);
    const isFormControl = React.useRef(false);
    const rootRef = React.useRef<HTMLDivElement>(null);

    React.useImperativeHandle(ref, () => rootRef.current!);

    React.useEffect(() => {
      if (rootRef.current) {
        isFormControl.current = !!rootRef.current.closest("form");
      }
    }, []);

    const setValue = React.useCallback(
      (newValue: string) => {
        if (!isControlledValue) {
          setInternalValue(newValue);
        }
        onValueChange?.(newValue);
      },
      [isControlledValue, onValueChange]
    );

    const setEditing = React.useCallback(
      (editing: boolean) => {
        if (!isControlledEditing) {
          setInternalEditing(editing);
        }
        onEditingChange?.(editing);
      },
      [isControlledEditing, onEditingChange]
    );

    const submit = React.useCallback(() => {
      const currentValue = resolvedValue;
      previousValueRef.current = currentValue;
      onValueSubmit?.(currentValue);
      setEditing(false);
    }, [resolvedValue, onValueSubmit, setEditing]);

    const cancel = React.useCallback(() => {
      const previousValue = previousValueRef.current;
      setValue(previousValue);
      onValueCancel?.(previousValue);
      setEditing(false);
    }, [setValue, onValueCancel, setEditing]);

    // NOT exposed on the context below — consumers enter edit mode through
    // `setIsEditing(true)`, which skips this snapshot of `previousValueRef`.
    // Kept because it documents the intended enter-edit path; wiring it up is a
    // behaviour change (cancel would then restore the value at edit-start).
    const _startEditing = React.useCallback(() => {
      if (disabled || readOnly) return;
      previousValueRef.current = resolvedValue;
      setEditing(true);
    }, [disabled, readOnly, resolvedValue, setEditing]);

    React.useEffect(() => {
      if (resolvedEditing) {
        requestAnimationFrame(() => {
          inputRef.current?.focus();
          textareaRef.current?.focus();
        });
      }
    }, [resolvedEditing]);

    return (
      <EditableContext.Provider
        value={{
          value: resolvedValue,
          setValue,
          isEditing: resolvedEditing,
          setIsEditing: setEditing,
          submit,
          cancel,
          disabled,
          readOnly,
          selectAllOnFocus,
          submitOnBlur,
          placeholder,
          inputRef,
          textareaRef,
          previousValueRef,
        }}
      >
        <div
          ref={rootRef}
          data-editing={resolvedEditing ? "" : undefined}
          data-disabled={disabled ? "" : undefined}
          data-readonly={readOnly ? "" : undefined}
          className={cn(
            "inline-flex items-center gap-1",
            disabled && "cursor-not-allowed opacity-50",
            className
          )}
          {...rootProps}
        >
          {children}
          {isFormControl.current && name && (
            <input type="hidden" name={name} value={resolvedValue} disabled={disabled} />
          )}
        </div>
      </EditableContext.Provider>
    );
  }
);

Editable.displayName = "Editable";

// =============================================================================
// Preview
// =============================================================================

const EditablePreview = React.forwardRef<HTMLSpanElement, EditablePreviewProps>(
  (props, ref) => {
    const context = useEditable("EditablePreview");

    if (context.isEditing) return null;

    return (
      <span
        ref={ref}
        role="button"
        tabIndex={context.disabled || context.readOnly ? undefined : 0}
        aria-disabled={context.disabled}
        data-placeholder={!context.value ? "" : undefined}
        className={cn(
          "cursor-pointer select-none rounded-[var(--radius)] px-2 py-1 hover:bg-accent transition-colors",
          !context.value && "text-muted-foreground italic",
          (context.disabled || context.readOnly) && "cursor-default hover:bg-transparent",
          props.className
        )}
        onClick={(event) => {
          props.onClick?.(event);
          if (!context.disabled && !context.readOnly) {
            context.setIsEditing(true);
          }
        }}
        onKeyDown={(event) => {
          props.onKeyDown?.(event);
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            if (!context.disabled && !context.readOnly) {
              context.setIsEditing(true);
            }
          }
        }}
        {...props}
      >
        {context.value || context.placeholder || "Click to edit"}
      </span>
    );
  }
);

EditablePreview.displayName = "EditablePreview";

// =============================================================================
// Input
// =============================================================================

const EditableInput = React.forwardRef<HTMLInputElement, EditableInputProps>(
  ({ inputSize = 'default', className, onChange, onKeyDown, onBlur, onFocus, ...props }, ref) => {
    const context = useEditable("EditableInput");

    const composedRef = React.useCallback(
      (node: HTMLInputElement | null) => {
        context.inputRef.current = node;
        if (typeof ref === "function") {
          ref(node);
        } else if (ref) {
          (ref as React.MutableRefObject<HTMLInputElement | null>).current = node;
        }
      },
      [ref, context.inputRef]
    );

    if (!context.isEditing) return null;

    return (
      <input
        type="text"
        ref={composedRef}
        value={context.value}
        disabled={context.disabled}
        aria-label="Edit value"
        // Share the global Input styling (crisp focus, proper surface) so
        // inline-edit fields match standalone inputs everywhere.
        // NOTE: spread `props` FIRST, then our handlers/className, so the
        // styled className + wrapped handlers always win (a trailing spread
        // would clobber them — that bug left the input unstyled/borderless).
        {...props}
        className={cn(inputClass(inputSize), className)}
        onChange={(event) => {
          onChange?.(event);
          context.setValue(event.target.value);
        }}
        onKeyDown={(event) => {
          onKeyDown?.(event);
          switch (event.key) {
            case "Enter":
              event.preventDefault();
              context.submit();
              break;
            case "Escape":
              event.preventDefault();
              context.cancel();
              break;
          }
        }}
        onBlur={(event) => {
          onBlur?.(event);
          if (context.submitOnBlur) {
            context.submit();
          }
        }}
        onFocus={(event) => {
          onFocus?.(event);
          if (context.selectAllOnFocus) {
            event.target.select();
          }
        }}
      />
    );
  }
);

EditableInput.displayName = "EditableInput";

// =============================================================================
// Textarea
// =============================================================================

const EditableTextarea = React.forwardRef<HTMLTextAreaElement, EditableTextareaProps>(
  (props, ref) => {
    const context = useEditable("EditableTextarea");

    const composedRef = React.useCallback(
      (node: HTMLTextAreaElement | null) => {
        context.textareaRef.current = node;
        if (typeof ref === "function") {
          ref(node);
        } else if (ref) {
          (ref as React.MutableRefObject<HTMLTextAreaElement | null>).current = node;
        }
      },
      [ref, context.textareaRef]
    );

    if (!context.isEditing) return null;

    return (
      <textarea
        ref={composedRef}
        value={context.value}
        disabled={context.disabled}
        aria-label="Edit value"
        // Share the global Textarea styling (crisp focus, proper surface).
        className={cn(TEXTAREA_CLASS, 'resize-none', props.className)}
        onChange={(event) => {
          props.onChange?.(event);
          context.setValue(event.target.value);
        }}
        onKeyDown={(event) => {
          props.onKeyDown?.(event);
          if (event.key === "Escape") {
            event.preventDefault();
            context.cancel();
          }
          // Submit on Ctrl+Enter or Meta+Enter
          if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            context.submit();
          }
        }}
        onBlur={(event) => {
          props.onBlur?.(event);
          if (context.submitOnBlur) {
            context.submit();
          }
        }}
        onFocus={(event) => {
          props.onFocus?.(event);
          if (context.selectAllOnFocus) {
            event.target.select();
          }
        }}
        {...props}
      />
    );
  }
);

EditableTextarea.displayName = "EditableTextarea";

// =============================================================================
// Exports
// =============================================================================

export {
  Editable,
  EditablePreview,
  EditableInput,
  EditableTextarea,
};

