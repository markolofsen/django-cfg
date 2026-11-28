import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { DateField, TimeField, DateTimeField } from '@djangocfg/ui-core/components';

/**
 * Native-engine date/time fields. The browser's `<input type="date|time|
 * datetime-local">` is the input engine — segmented keyboard entry, locale-aware
 * order, 12/24h by locale, arrow increment, and the OS wheel on touch, all free.
 * ui-core supplies the token-styled box + leading icon. `DateField` /
 * `DateTimeField` add a calendar popover (mouse only; touch defers to the OS
 * wheel); `TimeField` is a pure native segmented input.
 *
 * Wire values are ISO strings: `HH:mm`, `YYYY-MM-DD`, `YYYY-MM-DDTHH:mm`.
 */
const meta = {
  title: 'Packages/UI Core/Forms/DateTimeField',
  component: DateTimeField,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Native-engine, token-skinned date/time fields. DateField/DateTimeField pair a calendar popover with a native input; TimeField is pure native. Replaces the click-only DatePicker/TimePicker.',
      },
    },
  },
} satisfies Meta<typeof DateTimeField>;

export default meta;
type Story = StoryObj<typeof meta>;

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}

// --- TimeField -------------------------------------------------------------

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function TimeDemo() {
  const [value, setValue] = useState('');
  return (
    <div className="w-72 space-y-2">
      <TimeField value={value} onChange={setValue} aria-label="Time" />
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Time: Story = {
  render: () => <TimeDemo />,
};

function TimeWithValueDemo() {
  const [value, setValue] = useState('14:30');
  return (
    <div className="w-72 space-y-2">
      <TimeField value={value} onChange={setValue} aria-label="Time" />
      <p className="text-sm text-muted-foreground">
        12- vs 24-hour display follows the browser locale. Wire value stays 24h:{' '}
        <code className="font-mono">{value}</code>
      </p>
    </div>
  );
}

export const TimeWithValue: Story = {
  render: () => <TimeWithValueDemo />,
};

// --- DateField -------------------------------------------------------------

function DateDemo() {
  const [value, setValue] = useState('');
  return (
    <div className="w-72 space-y-2">
      <DateField value={value} onChange={setValue} aria-label="Date" />
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Date: Story = {
  render: () => <DateDemo />,
};

function DateWithRangeDemo() {
  const [value, setValue] = useState('');
  return (
    <div className="w-72 space-y-2">
      <DateField
        value={value}
        onChange={setValue}
        min="2026-01-01"
        max="2026-12-31"
        aria-label="Date"
      />
      <p className="text-sm text-muted-foreground">Bounded to 2026.</p>
    </div>
  );
}

export const DateWithRange: Story = {
  name: 'Date (min/max bounded)',
  render: () => <DateWithRangeDemo />,
};

// --- DateTimeField ---------------------------------------------------------

function DateTimeDemo() {
  const [value, setValue] = useState('');
  return (
    <div className="w-72 space-y-2">
      <DateTimeField value={value} onChange={setValue} aria-label="Date and time" />
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const DateTime: Story = {
  render: () => <DateTimeDemo />,
};

function DateTimeWithValueDemo() {
  const [value, setValue] = useState('2026-08-16T14:30');
  return (
    <div className="w-72 space-y-2">
      <DateTimeField value={value} onChange={setValue} aria-label="Date and time" />
      <p className="text-sm text-muted-foreground">
        Popover = calendar + a native time input beneath it.
      </p>
    </div>
  );
}

export const DateTimeWithValue: Story = {
  render: () => <DateTimeWithValueDemo />,
};

// --- States ----------------------------------------------------------------

function StatesDemo() {
  const [value, setValue] = useState('2026-08-16T09:15');
  return (
    <div className="grid w-72 gap-4">
      <Row label="Default">
        <DateTimeField value={value} onChange={setValue} aria-label="Date and time" />
      </Row>
      <Row label="Invalid">
        <DateTimeField value={value} onChange={setValue} invalid aria-label="Date and time" />
      </Row>
      <Row label="Disabled">
        <DateTimeField value={value} disabled aria-label="Date and time" />
      </Row>
    </div>
  );
}

export const States: Story = {
  render: () => <StatesDemo />,
};

function ConstrainedContainerDemo() {
  const [value, setValue] = useState('2026-08-16T01:40');
  return (
    <div className="relative h-80 w-96 overflow-hidden rounded-lg border p-4">
      <div className="absolute inset-x-4 bottom-4">
        <span className="mb-1.5 block text-xs font-medium text-muted-foreground">
          Run at
        </span>
        <DateTimeField value={value} onChange={setValue} aria-label="Run at" />
      </div>
    </div>
  );
}

/**
 * Regression guard for the "popover pokes out of the dialog" bug: the field sits
 * at the BOTTOM of a short, clipped container, so there's no room below. Radix's
 * default avoidCollisions flips the popover above the field; `collisionPadding`
 * keeps it off the edge. Open the picker — the whole calendar + time row must
 * stay visible.
 */
export const ConstrainedContainer: Story = {
  name: 'Near an edge (collision)',
  render: () => <ConstrainedContainerDemo />,
};

function FamilyDemo() {
  const [date, setDate] = useState('2026-08-16');
  const [time, setTime] = useState('14:30');
  const [dt, setDt] = useState('2026-08-16T14:30');
  return (
    <div className="grid w-72 gap-4">
      <Row label="DateField">
        <DateField value={date} onChange={setDate} aria-label="Date" />
      </Row>
      <Row label="TimeField">
        <TimeField value={time} onChange={setTime} aria-label="Time" />
      </Row>
      <Row label="DateTimeField">
        <DateTimeField value={dt} onChange={setDt} aria-label="Date and time" />
      </Row>
    </div>
  );
}

/**
 * All three fields together. Toggle the Storybook theme to confirm the token
 * surface + focus ring hold in both light and dark, and open the calendar to see
 * localized month/weekday names (from the app locale via react-day-picker).
 */
export const Family: Story = {
  render: () => <FamilyDemo />,
};
