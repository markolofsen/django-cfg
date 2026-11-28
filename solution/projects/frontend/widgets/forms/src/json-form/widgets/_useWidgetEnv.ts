/**
 * Internal helper that resolves widget-level environment from RJSF props:
 * - density (from formContext, default 'comfortable')
 * - effective `disabled` flag (combines props.disabled with `ui:disabledWhen`)
 *
 * Keeps each widget terse — no need to repeat the formContext + disabledWhen
 * boilerplate.
 */

import type { WidgetProps } from '@rjsf/utils';

import { evaluateDisabledWhen } from '../utils';
import type { DisabledWhenRule, JsonFormDensity } from '../types';

export interface WidgetEnv {
  density: JsonFormDensity;
  compact: boolean;
  disabled: boolean;
  /** Title-attribute text — in compact mode the description moves into a tooltip on the label/control. */
  tooltipText?: string;
}

export function useWidgetEnv(props: WidgetProps): WidgetEnv {
  const { disabled, readonly, formContext, uiSchema, schema } = props;
  const density: JsonFormDensity =
    (formContext?.density as JsonFormDensity | undefined) ?? 'comfortable';
  const compact = density === 'compact';

  const disabledWhen = uiSchema?.['ui:disabledWhen'] as DisabledWhenRule | undefined;
  const disabledByRule = evaluateDisabledWhen(disabledWhen, formContext?.formData);

  const tooltipText = compact
    ? (uiSchema?.['ui:description'] as string | undefined)
        ?? (schema?.description as string | undefined)
    : undefined;

  return {
    density,
    compact,
    disabled: Boolean(disabled || readonly || disabledByRule),
    tooltipText,
  };
}
