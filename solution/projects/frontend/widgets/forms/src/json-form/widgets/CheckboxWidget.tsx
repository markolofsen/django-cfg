import React from 'react';

import { Checkbox } from '@djangocfg/ui-core/components';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Checkbox widget for JSON Schema Form
 * Handles boolean fields
 */
export function CheckboxWidget(props: WidgetProps) {
  const { id, value, autofocus, onChange, onBlur, onFocus } = props;
  const { disabled, tooltipText } = useWidgetEnv(props);

  const handleChange = (checked: boolean) => {
    onChange(checked);
  };

  return (
    <Checkbox
      id={id}
      checked={value || false}
      disabled={disabled}
      autoFocus={autofocus}
      onCheckedChange={handleChange}
      onBlur={() => onBlur(id, value)}
      onFocus={() => onFocus(id, value)}
      title={tooltipText}
    />
  );
}
