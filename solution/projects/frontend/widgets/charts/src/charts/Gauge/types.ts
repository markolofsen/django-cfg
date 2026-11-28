import * as React from 'react';

export type GaugeState = 'indeterminate' | 'complete' | 'loading';

export interface GaugeProps extends React.ComponentProps<'div'> {
  value?: number | null | undefined;
  getValueText?(value: number, min: number, max: number): string;
  min?: number;
  max?: number;
  size?: number;
  thickness?: number;
  startAngle?: number;
  endAngle?: number;
  asChild?: boolean;
}

export interface GaugeContextValue {
  value: number | null;
  valueText: string | undefined;
  max: number;
  min: number;
  state: GaugeState;
  radius: number;
  thickness: number;
  size: number;
  center: number;
  percentage: number | null;
  startAngle: number;
  endAngle: number;
  arcLength: number;
  arcCenterY: number;
  valueTextId?: string;
  labelId?: string;
}
