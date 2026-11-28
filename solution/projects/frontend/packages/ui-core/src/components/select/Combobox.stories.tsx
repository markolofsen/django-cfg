import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Apple, Banana, Cherry, Citrus, Grape } from 'lucide-react';
import { Combobox, Label, type ComboboxOption } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/Combobox',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Searchable single-select with optional icons, badges and descriptions. Pairs with `ComboboxAsync` for parent-owned async search.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const FRUITS: ComboboxOption[] = [
  { value: 'apple', label: 'Apple', icon: Apple },
  { value: 'banana', label: 'Banana', icon: Banana },
  { value: 'cherry', label: 'Cherry', icon: Cherry },
  { value: 'grape', label: 'Grape', icon: Grape },
  { value: 'orange', label: 'Orange', icon: Citrus },
];

function DefaultHost() {
  const [value, setValue] = useState('');
  return (
    <div className="grid w-72 gap-1.5">
      <Label>Fruit</Label>
      <Combobox
        options={FRUITS.map(({ icon: _icon, ...rest }) => rest)}
        value={value}
        onValueChange={setValue}
        placeholder="Pick a fruit"
      />
      <p className="text-xs text-muted-foreground">Selected: {value || '(none)'}</p>
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultHost />,
};

function WithSearchHost() {
  const [value, setValue] = useState('cherry');
  return (
    <div className="grid w-72 gap-1.5">
      <Label>Fruit</Label>
      <Combobox
        options={FRUITS}
        value={value}
        onValueChange={setValue}
        placeholder="Pick a fruit"
        searchPlaceholder="Type to filter…"
        emptyText="No fruits match"
      />
    </div>
  );
}

export const WithSearch: Story = {
  render: () => <WithSearchHost />,
};

// Combobox itself doesn't render group headings (flat list), but renderOption
// lets us simulate a categorised display by prefixing labels. The closest
// real-world pattern is wrapping options with category metadata in the label.
function WithGroupsHost() {
  const [value, setValue] = useState('');
  const grouped: ComboboxOption[] = [
    { value: 'apple', label: 'Apple', description: 'Citrus-free', badge: 'Fruit' },
    { value: 'banana', label: 'Banana', description: 'Tropical', badge: 'Fruit' },
    { value: 'carrot', label: 'Carrot', description: 'Root', badge: 'Veggie' },
    { value: 'broccoli', label: 'Broccoli', description: 'Cruciferous', badge: 'Veggie' },
  ];
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Produce</Label>
      <Combobox
        options={grouped}
        value={value}
        onValueChange={setValue}
        placeholder="Pick produce"
      />
    </div>
  );
}

export const WithGroups: Story = {
  render: () => <WithGroupsHost />,
};

export const Disabled: Story = {
  render: () => (
    <div className="grid w-72 gap-1.5">
      <Label>Fruit</Label>
      <Combobox
        options={FRUITS}
        value="apple"
        disabled
        placeholder="Pick a fruit"
      />
    </div>
  ),
};

function ClearableHost() {
  const [value, setValue] = useState('cherry');
  return (
    <div className="grid w-72 gap-2">
      <Label>Fruit</Label>
      <Combobox
        options={FRUITS}
        value={value}
        onValueChange={setValue}
        placeholder="Pick a fruit"
      />
      <button
        type="button"
        className="text-xs underline text-muted-foreground self-start"
        onClick={() => setValue('')}
        disabled={!value}
      >
        Clear selection
      </button>
    </div>
  );
}

export const Clearable: Story = {
  render: () => <ClearableHost />,
};

/* ---------------------------------------------------------------------------
 * Long list, pinned to the bottom edge
 * ------------------------------------------------------------------------ */

/** Car makes, in the order a real facet count returns them. */
const MAKES: ComboboxOption[] = [
  'Volkswagen', 'Toyota', 'Audi', 'Mercedes-Benz', 'Ford', 'Honda', 'Nissan',
  'Peugeot', 'Suzuki', 'Renault', 'Volvo', 'Chevrolet', 'Opel', 'Fiat',
  'Skoda', 'Mazda', 'Genesis', 'Land Rover', 'Jeep', 'Mitsubishi', 'Porsche',
  'Subaru', 'Lexus', 'Mini', 'Seat', 'Citroen', 'Dacia', 'Chrysler', 'Dodge',
  'Cadillac', 'Jaguar', 'Alfa Romeo', 'Infiniti', 'Acura', 'Buick', 'Lincoln',
  'Ram', 'GMC', 'Tesla', 'Polestar', 'Bentley', 'Maserati', 'Ferrari',
  'Lamborghini', 'Aston Martin', 'Rolls-Royce', 'Lotus', 'Bugatti',
].map((label) => ({ value: label.toLowerCase().replace(/\s+/g, '-'), label }));

/**
 * The trigger sits flush against the bottom of the viewport, so the popover has
 * no room below and Radix flips it above. That is the arrangement that used to
 * break: the panel opened taller than the gap to the top of the window and its
 * first rows were clipped by the viewport, unreachable by scrolling.
 *
 * What to check: every row is reachable, the top of the list is not cut off,
 * and the panel keeps a small gap from the window edge (`collisionPadding`).
 */
function BottomEdgeHost() {
  const [value, setValue] = useState('');
  return (
    <div className="flex h-screen flex-col justify-end p-4">
      <div className="grid w-72 gap-1.5">
        <Label>Make</Label>
        <Combobox
          options={MAKES}
          value={value}
          onValueChange={setValue}
          placeholder="Any make"
          searchPlaceholder="Search make"
        />
      </div>
    </div>
  );
}

export const BottomEdge: Story = {
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story:
          'A long list opened from the bottom edge of the viewport. The popover flips above the trigger and must stay inside the window, scrolling rather than clipping.',
      },
    },
  },
  render: () => <BottomEdgeHost />,
};

/**
 * Opens with a selection far down the list. cmdk highlights the row it is given
 * and scrolls it into view, so the panel should open showing "Porsche" — not at
 * the top with the selection somewhere below the fold.
 *
 * Arrow keys must still move the highlight from there; a controlled highlight
 * with no change handler would freeze it, which is the other half of this test.
 */
function ScrollsToSelectionHost() {
  const [value, setValue] = useState('porsche');
  return (
    <div className="grid w-72 gap-1.5 p-4">
      <Label>Make</Label>
      <Combobox
        options={MAKES}
        value={value}
        onValueChange={setValue}
        placeholder="Any make"
        searchPlaceholder="Search make"
      />
      <p className="text-xs text-muted-foreground">Selected: {value || '(none)'}</p>
    </div>
  );
}

export const ScrollsToSelection: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Opens scrolled to the selected row rather than to the top of the list. Arrow keys move the highlight from there.',
      },
    },
  },
  render: () => <ScrollsToSelectionHost />,
};
