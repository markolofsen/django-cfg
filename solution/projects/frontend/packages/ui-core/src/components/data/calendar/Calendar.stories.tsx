import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Calendar,
  DatePicker,
  DateRangePicker,
  type DateRange,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Calendar',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

function CalendarSingle() {
  const [date, setDate] = useState<Date | undefined>(new Date());
  return (
    <Calendar
      mode="single"
      selected={date}
      onSelect={setDate}
      className="rounded-md border border-border"
    />
  );
}

function CalendarRange() {
  const [range, setRange] = useState<DateRange | undefined>({
    from: new Date(),
    to: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
  });
  return (
    <Calendar
      mode="range"
      selected={range}
      onSelect={setRange}
      className="rounded-md border border-border"
      numberOfMonths={2}
    />
  );
}

function CalendarMultiple() {
  const [dates, setDates] = useState<Date[] | undefined>([]);
  return (
    <Calendar
      mode="multiple"
      selected={dates}
      onSelect={setDates}
      className="rounded-md border border-border"
    />
  );
}

function DatePickerHost() {
  const [date, setDate] = useState<Date | undefined>();
  return (
    <div className="w-72">
      <DatePicker value={date} onChange={setDate} placeholder="Pick a date" />
    </div>
  );
}

function DatePickerLabeled() {
  const [date, setDate] = useState<Date | undefined>();
  return (
    <div className="w-72 space-y-2">
      <label className="text-sm font-medium">Date of birth</label>
      <DatePicker
        value={date}
        onChange={setDate}
        placeholder="Select your birth date"
      />
    </div>
  );
}

function RangePickerHost() {
  const [range, setRange] = useState<DateRange | undefined>();
  return (
    <div className="w-80">
      <DateRangePicker
        value={range}
        onChange={setRange}
        placeholder="Select date range"
      />
    </div>
  );
}

function RangePickerLabeled() {
  const [range, setRange] = useState<DateRange | undefined>();
  return (
    <div className="w-80 space-y-2">
      <label className="text-sm font-medium">Booking dates</label>
      <DateRangePicker
        value={range}
        onChange={setRange}
        placeholder="Check-in — Check-out"
        numberOfMonths={2}
      />
    </div>
  );
}

function DatePickerDisabled() {
  const [date, setDate] = useState<Date | undefined>();
  return (
    <div className="w-72">
      <DatePicker
        value={date}
        onChange={setDate}
        placeholder="Pick a date"
        disabled
      />
    </div>
  );
}

export const Single: Story = { render: () => <CalendarSingle /> };
export const Range: Story = { render: () => <CalendarRange /> };
export const Multiple: Story = { render: () => <CalendarMultiple /> };
export const Picker: Story = { render: () => <DatePickerHost /> };
export const PickerWithLabel: Story = { render: () => <DatePickerLabeled /> };
export const RangePicker: Story = { render: () => <RangePickerHost /> };
export const RangePickerWithPresets: Story = { render: () => <RangePickerLabeled /> };
export const Disabled: Story = { render: () => <DatePickerDisabled /> };
