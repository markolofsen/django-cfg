import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Car, ChevronDown, Fuel, Gauge, SlidersHorizontal } from 'lucide-react';

import { FilterBar, FilterButton } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/FilterButton',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'A filter control in a toolbar. Always inside a `FilterBar`, which owns the row height and the container the labels collapse against.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

/** The row as a catalogue actually uses it: one control that opens the panel,
 *  then a pill per facet. */
function ToolbarHost() {
  const [body, setBody] = useState<string | undefined>('SUV');
  return (
    <FilterBar>
      <FilterButton variant="solid" icon={SlidersHorizontal} count={3}>
        Filters
      </FilterButton>
      <FilterButton
        icon={Car}
        trailingIcon={ChevronDown}
        value={body}
        active={Boolean(body)}
        onClick={() => setBody(body ? undefined : 'SUV')}
      >
        Body type
      </FilterButton>
      <FilterButton icon={Fuel} trailingIcon={ChevronDown} count={6}>
        Fuel
      </FilterButton>
      <FilterButton icon={Gauge} trailingIcon={ChevronDown}>
        Mileage
      </FilterButton>
    </FilterBar>
  );
}

export const Toolbar: Story = {
  render: () => <ToolbarHost />,
};

/**
 * The labels collapse when the ROW is tight — not when the window is.
 *
 * Both frames below sit in the same viewport; only the column width differs.
 * The narrow one shows what a phone would show, and equally what a wide monitor
 * shows when the toolbar lives in a narrow column — the case a viewport media
 * query gets wrong.
 *
 * "Body type" keeps its label because it carries an ANSWER ("SUV"). An icon can
 * stand in for a question; it cannot stand in for the answer to one.
 */
export const CollapsesWithTheRow: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Label collapse is driven by a container query on the row, so the same toolbar adapts inside a narrow column on a wide screen.',
      },
    },
  },
  render: () => (
    <div className="space-y-8">
      {[
        { label: 'roomy row — 44rem', width: '44rem' },
        { label: 'tight row — 22rem', width: '22rem' },
      ].map(({ label, width }) => (
        <div key={width} className="space-y-1.5">
          <span className="text-xs text-muted-foreground">{label}</span>
          <div style={{ width, maxWidth: '100%' }}>
            <ToolbarHost />
          </div>
        </div>
      ))}
    </div>
  ),
};

/** `overflow="scroll"` keeps the row on one line — for a toolbar under a header,
 *  where a second line would push the content down. */
export const Scrolling: Story = {
  render: () => (
    <div style={{ width: '22rem', maxWidth: '100%' }}>
      <FilterBar overflow="scroll">
        {['Make', 'Body type', 'Fuel', 'Transmission', 'Year', 'Colour'].map((facet) => (
          <FilterButton key={facet} icon={Car} trailingIcon={ChevronDown}>
            {facet}
          </FilterButton>
        ))}
      </FilterBar>
    </div>
  ),
};
