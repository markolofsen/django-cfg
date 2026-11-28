import React from 'react';

import { Switch } from '@djangocfg/ui-core/components';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Switch toggle widget for JSON Schema Form
 * Alternative boolean input
 */
export function SwitchWidget(props: WidgetProps) {
  const { id, value, onChange, onBlur, onFocus } = props;
  const { disabled, tooltipText } = useWidgetEnv(props);

  const handleChange = (checked: boolean) => {
    onChange(checked);
  };

  return (
    <Switch
      id={id}
      checked={value || false}
      disabled={disabled}
      onCheckedChange={handleChange}
      onBlur={() => onBlur(id, value)}
      onFocus={() => onFocus(id, value)}
      title={tooltipText}
    />
  );
}
