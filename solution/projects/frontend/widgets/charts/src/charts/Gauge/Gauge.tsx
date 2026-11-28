'use client';

import { Slot as SlotPrimitive } from '@radix-ui/react-slot';
import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import type { GaugeProps, GaugeContextValue, GaugeState } from './types';

const GAUGE_NAME = 'Gauge';
const INDICATOR_NAME = 'GaugeIndicator';
const TRACK_NAME = 'GaugeTrack';
const RANGE_NAME = 'GaugeRange';
const VALUE_TEXT_NAME = 'GaugeValueText';
const LABEL_NAME = 'GaugeLabel';

const DEFAULT_MAX = 100;
const DEFAULT_START_ANGLE = 0;
const DEFAULT_END_ANGLE = 360;

function getGaugeState(value: number | undefined | null, maxValue: number): GaugeState {
  return value == null
    ? 'indeterminate'
    : value === maxValue
      ? 'complete'
      : 'loading';
}

function getIsValidNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function getIsValidMaxNumber(max: unknown): max is number {
  return getIsValidNumber(max) && max > 0;
}

function getIsValidValueNumber(value: unknown, min: number, max: number): value is number {
  return getIsValidNumber(value) && value <= max && value >= min;
}

function getDefaultValueText(value: number, min: number, max: number): string {
  const percentage = max === min ? 100 : ((value - min) / (max - min)) * 100;
  return Math.round(percentage).toString();
}

function getNormalizedAngle(angle: number) {
  return ((angle % 360) + 360) % 360;
}

function polarToCartesian(centerX: number, centerY: number, radius: number, angleInDegrees: number) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

function describeArc(x: number, y: number, radius: number, startAngle: number, endAngle: number) {
  const angleDiff = endAngle - startAngle;

  if (Math.abs(angleDiff) >= 360) {
    const start = polarToCartesian(x, y, radius, startAngle);
    const mid = polarToCartesian(x, y, radius, startAngle + 180);
    return [
      'M', start.x, start.y,
      'A', radius, radius, 0, 0, 1, mid.x, mid.y,
      'A', radius, radius, 0, 0, 1, start.x, start.y,
    ].join(' ');
  }

  const start = polarToCartesian(x, y, radius, startAngle);
  const end = polarToCartesian(x, y, radius, endAngle);
  const largeArcFlag = angleDiff <= 180 ? '0' : '1';

  return [
    'M', start.x, start.y,
    'A', radius, radius, 0, largeArcFlag, 1, end.x, end.y,
  ].join(' ');
}

const GaugeContext = React.createContext<GaugeContextValue | null>(null);

function useGaugeContext(consumerName: string) {
  const context = React.useContext(GaugeContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within \`${GAUGE_NAME}\``);
  }
  return context;
}

export function Gauge(props: GaugeProps) {
  const {
    value: valueProp = null,
    getValueText = getDefaultValueText,
    min: minProp = 0,
    max: maxProp,
    size = 120,
    thickness = 8,
    startAngle = DEFAULT_START_ANGLE,
    endAngle = DEFAULT_END_ANGLE,
    asChild,
    className,
    ...rootProps
  } = props;

  if ((maxProp || maxProp === 0) && !getIsValidMaxNumber(maxProp)) {
    if (process.env.NODE_ENV !== 'production') {
      console.error(`Invalid prop \`max\` of value \`${maxProp}\` supplied to \`${GAUGE_NAME}\`. Only numbers greater than 0 are valid. Defaulting to ${DEFAULT_MAX}.`);
    }
  }

  const rawMax = getIsValidMaxNumber(maxProp) ? maxProp : DEFAULT_MAX;
  const min = getIsValidNumber(minProp) ? minProp : 0;
  const max = rawMax <= min ? min + 1 : rawMax;

  if (process.env.NODE_ENV !== 'production' && thickness >= size) {
    console.warn(`Gauge: thickness (${thickness}) should be less than size (${size}) for proper rendering.`);
  }

  if (valueProp !== null && !getIsValidValueNumber(valueProp, min, max)) {
    if (process.env.NODE_ENV !== 'production') {
      console.error(`Invalid prop \`value\` of value \`${valueProp}\` supplied to \`${GAUGE_NAME}\`. The \`value\` prop must be a number between \`min\` and \`max\` (inclusive), or \`null\`/\`undefined\` for indeterminate state. The value will be clamped to the valid range.`);
    }
  }

  const value = getIsValidValueNumber(valueProp, min, max)
    ? valueProp
    : getIsValidNumber(valueProp) && valueProp > max
      ? max
      : getIsValidNumber(valueProp) && valueProp < min
        ? min
        : null;

  const valueText = getIsValidNumber(value) ? getValueText(value, min, max) : undefined;
  const state = getGaugeState(value, max);
  const radius = Math.max(0, (size - thickness) / 2);
  const center = size / 2;

  const angleDiff = Math.abs(endAngle - startAngle);
  const arcLength = (Math.min(angleDiff, 360) / 360) * (2 * Math.PI * radius);

  const percentage = getIsValidNumber(value)
    ? max === min
      ? 1
      : (value - min) / (max - min)
    : null;

  const angleDiffDeg = Math.abs(endAngle - startAngle);
  const isFullCircle = angleDiffDeg >= 360;

  let arcCenterY = center;
  if (!isFullCircle) {
    const startRad = (startAngle * Math.PI) / 180;
    const endRad = (endAngle * Math.PI) / 180;

    const startY = center - radius * Math.cos(startRad);
    const endY = center - radius * Math.cos(endRad);

    let minY = Math.min(startY, endY);
    let maxY = Math.max(startY, endY);

    const normStart = getNormalizedAngle(startAngle);
    const normEnd = getNormalizedAngle(endAngle);

    const includesTop =
      normStart > normEnd
        ? normStart <= 270 || normEnd >= 270
        : normStart <= 270 && normEnd >= 270;
    const includesBottom =
      normStart > normEnd
        ? normStart <= 90 || normEnd >= 90
        : normStart <= 90 && normEnd >= 90;

    if (includesTop) minY = Math.min(minY, center - radius);
    if (includesBottom) maxY = Math.max(maxY, center + radius);

    arcCenterY = (minY + maxY) / 2;
  }

  const labelId = React.useId();
  const valueTextId = React.useId();

  const contextValue = React.useMemo<GaugeContextValue>(
    () => ({
      value,
      valueText,
      max,
      min,
      state,
      radius,
      thickness,
      size,
      center,
      percentage,
      startAngle,
      endAngle,
      arcLength,
      arcCenterY,
      valueTextId,
      labelId,
    }),
    [value, valueText, max, min, state, radius, thickness, size, center, percentage, startAngle, endAngle, arcLength, arcCenterY, valueTextId, labelId]
  );

  const RootPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <GaugeContext.Provider value={contextValue}>
      <RootPrimitive
        role="meter"
        aria-describedby={valueText ? valueTextId : undefined}
        aria-labelledby={labelId}
        aria-valuemax={max}
        aria-valuemin={min}
        aria-valuenow={getIsValidNumber(value) ? value : undefined}
        aria-valuetext={valueText}
        data-state={state}
        data-value={value ?? undefined}
        data-max={max}
        data-min={min}
        data-percentage={percentage}
        {...rootProps}
        className={cn(
          'relative inline-flex w-fit flex-col items-center justify-center',
          className
        )}
      />
    </GaugeContext.Provider>
  );
}

Gauge.displayName = GAUGE_NAME;

export function GaugeIndicator(props: React.ComponentProps<'svg'>) {
  const { className, ...indicatorProps } = props;

  const { size, state, value, max, min, percentage } = useGaugeContext(INDICATOR_NAME);

  return (
    <svg
      aria-hidden="true"
      focusable="false"
      viewBox={`0 0 ${size} ${size}`}
      data-state={state}
      data-value={value ?? undefined}
      data-max={max}
      data-min={min}
      data-percentage={percentage}
      width={size}
      height={size}
      {...indicatorProps}
      className={cn('transform', className)}
    />
  );
}

GaugeIndicator.displayName = INDICATOR_NAME;

type PathProps = React.ComponentProps<'path'>;

export function GaugeTrack(props: PathProps) {
  const { className, ...trackProps } = props;

  const { center, radius, startAngle, endAngle, thickness, state } = useGaugeContext(TRACK_NAME);

  const pathData = describeArc(center, center, radius, startAngle, endAngle);

  return (
    <path
      data-state={state}
      d={pathData}
      fill="none"
      stroke="currentColor"
      strokeWidth={thickness}
      strokeLinecap="round"
      vectorEffect="non-scaling-stroke"
      {...trackProps}
      className={cn('text-muted-foreground/20', className)}
    />
  );
}

GaugeTrack.displayName = TRACK_NAME;

export function GaugeRange(props: PathProps) {
  const { className, ...rangeProps } = props;

  const {
    center,
    radius,
    startAngle,
    endAngle,
    value,
    max,
    min,
    state,
    thickness,
    arcLength,
    percentage,
  } = useGaugeContext(RANGE_NAME);

  const pathData = describeArc(center, center, radius, startAngle, endAngle);

  const strokeDasharray = arcLength;
  const strokeDashoffset =
    state === 'indeterminate'
      ? 0
      : percentage !== null
        ? arcLength - percentage * arcLength
        : arcLength;

  return (
    <path
      data-state={state}
      data-value={value ?? undefined}
      data-max={max}
      data-min={min}
      d={pathData}
      fill="none"
      stroke="currentColor"
      strokeWidth={thickness}
      strokeLinecap="round"
      strokeDasharray={strokeDasharray}
      strokeDashoffset={strokeDashoffset}
      vectorEffect="non-scaling-stroke"
      {...rangeProps}
      className={cn(
        'text-primary transition-[stroke-dashoffset] duration-700 ease-out',
        className
      )}
    />
  );
}

GaugeRange.displayName = RANGE_NAME;

interface DivProps extends React.ComponentProps<'div'> {
  asChild?: boolean;
}

export function GaugeValueText(props: DivProps) {
  const { asChild, className, children, style, ...valueTextProps } = props;

  const { valueTextId, state, arcCenterY, valueText } = useGaugeContext(VALUE_TEXT_NAME);

  const ValueTextPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <ValueTextPrimitive
      id={valueTextId}
      data-state={state}
      {...valueTextProps}
      style={{
        top: `${arcCenterY}px`,
        ...style,
      }}
      className={cn(
        'absolute right-0 left-0 flex -translate-y-1/2 items-center justify-center font-semibold text-2xl',
        className
      )}
    >
      {children ?? valueText}
    </ValueTextPrimitive>
  );
}

GaugeValueText.displayName = VALUE_TEXT_NAME;

export function GaugeLabel(props: DivProps) {
  const { asChild, className, ...labelProps } = props;

  const { labelId, state } = useGaugeContext(LABEL_NAME);

  const LabelPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <LabelPrimitive
      id={labelId}
      data-state={state}
      {...labelProps}
      className={cn(
        'mt-2 font-medium text-muted-foreground text-sm',
        className
      )}
    />
  );
}

GaugeLabel.displayName = LABEL_NAME;

export function GaugeCombined(props: GaugeProps) {
  return (
    <Gauge {...props}>
      <GaugeIndicator>
        <GaugeTrack />
        <GaugeRange />
      </GaugeIndicator>
      <GaugeValueText />
    </Gauge>
  );
}

GaugeCombined.displayName = 'GaugeCombined';
