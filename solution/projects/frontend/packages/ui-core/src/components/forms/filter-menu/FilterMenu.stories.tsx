import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Car, Fuel, Gauge, Palette } from 'lucide-react';

import {
  FilterBar,
  FilterMenu,
  Label,
  Slider,
  type FilterMenuOption,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/FilterMenu',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'A filter trigger and the menu it opens. Pass `options` for a list, or `children` for a body of your own.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const opts = (labels: string[]): FilterMenuOption[] =>
  labels.map((label) => ({ value: label.toLowerCase().replace(/\s+/g, '-'), label }));

const BODY_TYPES = opts(['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Wagon']);

const MAKES: FilterMenuOption[] = [
  'Volkswagen', 'Toyota', 'Audi', 'Mercedes-Benz', 'Ford', 'Honda', 'Nissan',
  'Peugeot', 'Suzuki', 'Renault', 'Volvo', 'Chevrolet', 'Opel', 'Fiat',
  'Skoda', 'Mazda', 'Genesis', 'Land Rover', 'Jeep', 'Mitsubishi', 'Porsche',
].map((label, i) => ({
  value: label.toLowerCase().replace(/\s+/g, '-'),
  label,
  count: 120 - i * 4,
}));

/**
 * The search field appears on its own once a list outgrows its popover —
 * around ten options, where the reader would otherwise be scrolling blind.
 *
 * Both menus below are the same component with the same props. "Body type" has
 * five options and opens as a plain list; "Make" has twenty-one and opens with
 * a search field. Nobody had to decide which.
 */
function AutoSearchHost() {
  const [make, setMake] = useState<string | null>(null);
  const [body, setBody] = useState<string | null>('suv');
  return (
    <FilterBar>
      <FilterMenu
        label="Body type"
        icon={Car}
        options={BODY_TYPES}
        value={body}
        onValueChange={setBody}
      />
      <FilterMenu
        label="Make"
        icon={Gauge}
        options={MAKES}
        value={make}
        onValueChange={setMake}
      />
    </FilterBar>
  );
}

export const AutoSearch: Story = {
  render: () => <AutoSearchHost />,
};

/**
 * `children` replaces the list entirely. The trigger, the popover and the open
 * state stay with the component; the body is whatever the filter actually
 * needs — here a price range, which no list of options can express.
 */
function CustomBodyHost() {
  const [price, setPrice] = useState([15000]);
  return (
    <FilterBar>
      <FilterMenu label="Price" icon={Palette} contentClassName="w-72 p-4">
        <div className="space-y-4">
          <Label>Up to ${(price[0] ?? 0).toLocaleString()}</Label>
          <Slider value={price} onValueChange={setPrice} min={0} max={80000} step={1000} />
        </div>
      </FilterMenu>
      <FilterMenu label="Fuel" icon={Fuel} options={opts(['Petrol', 'Diesel', 'Hybrid', 'Electric'])} />
    </FilterBar>
  );
}

export const CustomBody: Story = {
  render: () => <CustomBodyHost />,
};

/** `searchable` overrides the threshold in either direction. */
export const ForcedSearch: Story = {
  render: () => (
    <FilterBar>
      <FilterMenu label="Always" icon={Car} options={BODY_TYPES} searchable />
      <FilterMenu label="Never" icon={Gauge} options={MAKES} searchable={false} />
      <FilterMenu label="From 3" icon={Fuel} options={BODY_TYPES} searchable={3} />
    </FilterBar>
  ),
};
