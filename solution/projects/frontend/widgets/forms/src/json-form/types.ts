import type { RJSFSchema, RJSFValidationError, UiSchema } from '@rjsf/utils';
import type { IChangeEvent, FormProps } from '@rjsf/core';
import type {
  CustomJsonSchema7,
  CustomJsonUiSchema7,
  CustomJsonUiDisabledWhenRule,
  CustomJsonUiGroup,
} from '@djangocfg/ui-core/lib';

/** Visual density for form controls. */
export type JsonFormDensity = 'comfortable' | 'compact';

/**
 * Aliases that point to the portable schema types in `@djangocfg/ui-core/lib`.
 * Kept under their old short names for back-compat — new code can import the
 * `CustomJson*` originals directly from ui-core.
 */
export type DisabledWhenRule = CustomJsonUiDisabledWhenRule;
export type UiGroup = CustomJsonUiGroup;

/** What we put into RJSF's `formContext` so widgets/templates can react to global form state. */
export interface JsonFormContext {
  density: JsonFormDensity;
  /** Latest form data — used by `evaluateDisabledWhen`. */
  formData: unknown;
}

/**
 * JSON Schema Form props interface
 */
export interface JsonSchemaFormProps<T = unknown>
  extends Omit<Partial<FormProps<T>>, 'schema' | 'uiSchema'> {
  /**
   * JSON Schema that defines the form structure. Accepts either RJSF's
   * `RJSFSchema` directly or our portable `CustomJsonSchema7` from
   * `@djangocfg/ui-core/lib` — both are cast to RJSF internally.
   */
  schema: RJSFSchema | CustomJsonSchema7;

  /** UI Schema for customizing the form appearance. Same dual-shape acceptance as `schema`. */
  uiSchema?: UiSchema | CustomJsonUiSchema7;

  /** Initial form data */
  formData?: T;

  /** Callback when form is submitted */
  onSubmit?: (data: IChangeEvent<T>) => void;

  /** Callback when form data changes */
  onChange?: (data: IChangeEvent<T>) => void;

  /** Callback when form has validation errors */
  onError?: (errors: RJSFValidationError[]) => void;

  /** Whether to show error list at the top of form */
  showErrorList?: false | 'top' | 'bottom';

  /** Whether to live validate on change */
  liveValidate?: boolean;

  /** Whether the form is disabled */
  disabled?: boolean;

  /** Whether the form is read-only */
  readonly?: boolean;

  /** Custom CSS class name */
  className?: string;

  /** Whether to show submit button */
  showSubmitButton?: boolean;

  /** Submit button text */
  submitButtonText?: string;

  /** Visual density preset. `'compact'` shrinks rows and hides description text (moves it to label `title=` tooltip). */
  density?: JsonFormDensity;
}

/**
 * Field template props
 */
export interface FieldTemplateProps {
  id: string;
  label: string;
  required: boolean;
  description?: string;
  errors?: React.ReactNode;
  help?: string;
  displayLabel?: boolean;
  children: React.ReactNode;
  classNames?: string;
  rawErrors?: string[];
  schema: RJSFSchema;
}

/**
 * Widget props base interface
 */
export interface BaseWidgetProps {
  id: string;
  value: unknown;
  required: boolean;
  disabled: boolean;
  readonly: boolean;
  autofocus: boolean;
  onChange: (value: unknown) => void;
  onBlur: (id: string, value: unknown) => void;
  onFocus: (id: string, value: unknown) => void;
  /** RJSF's `ui:options` bag — open by design; widgets read the keys they know. */
  options: Record<string, unknown>;
  schema: RJSFSchema;
  label: string;
  placeholder?: string;
  rawErrors?: string[];
}
