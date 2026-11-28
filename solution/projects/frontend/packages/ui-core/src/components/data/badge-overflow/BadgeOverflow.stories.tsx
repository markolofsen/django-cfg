import type { Meta, StoryObj } from '@storybook/react-vite';
import { Badge, BadgeOverflow } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/BadgeOverflow',
  component: BadgeOverflow,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A container that measures and truncates badges into a limited number of lines with an overflow counter.',
      },
    },
  },
  argTypes: {
    lineCount: { control: 'number' },
  },
  args: {
    items: [],
    renderBadge: () => null,
  },
} satisfies Meta<typeof BadgeOverflow>;

export default meta;
type Story = StoryObj<typeof meta>;

const items = [
  'React', 'TypeScript', 'Tailwind', 'Node.js', 'PostgreSQL',
  'Docker', 'GraphQL', 'Redis', 'Next.js', 'Vite',
];

export const Default: Story = {
  render: () => (
    <div className="w-80">
      <BadgeOverflow
        items={items}
        renderBadge={(item) => (
          <Badge variant="secondary">{item}</Badge>
        )}
      />
    </div>
  ),
};

export const SingleLine: Story = {
  render: () => (
    <div className="w-80">
      <BadgeOverflow
        items={items}
        lineCount={1}
        renderBadge={(item) => (
          <Badge variant="outline">{item}</Badge>
        )}
      />
    </div>
  ),
};

export const TwoLines: Story = {
  render: () => (
    <div className="w-80">
      <BadgeOverflow
        items={items}
        lineCount={2}
        renderBadge={(item) => (
          <Badge variant="secondary">{item}</Badge>
        )}
      />
    </div>
  ),
};

export const CustomOverflow: Story = {
  render: () => (
    <div className="w-80">
      <BadgeOverflow
        items={items}
        lineCount={1}
        renderBadge={(item) => (
          <Badge variant="default">{item}</Badge>
        )}
        renderOverflow={(count) => (
          <Badge variant="destructive">+{count} more</Badge>
        )}
      />
    </div>
  ),
};

export const WithObjects: Story = {
  render: () => (
    <div className="w-80">
      <BadgeOverflow
        items={[
          { id: 1, name: 'Feature' },
          { id: 2, name: 'Bugfix' },
          { id: 3, name: 'Refactor' },
          { id: 4, name: 'Docs' },
          { id: 5, name: 'Tests' },
          { id: 6, name: 'CI/CD' },
        ]}
        getBadgeLabel={(item) => item.name}
        lineCount={1}
        renderBadge={(item) => (
          <Badge variant="outline">{item.name}</Badge>
        )}
      />
    </div>
  ),
};
