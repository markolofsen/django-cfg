import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  ScrollSpy,
  ScrollSpyNav,
  ScrollSpyNavItem,
  ScrollSpySection,
} from '.';

const meta = {
  title: 'Widgets/Overlay/ScrollSpy',
  component: ScrollSpy,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'Navigation that highlights the active section based on scroll position.',
      },
    },
  },
  args: {
    children: null,
  },
} satisfies Meta<typeof ScrollSpy>;

export default meta;
type Story = StoryObj<typeof meta>;

const sections = [
  { id: 'intro', label: 'Introduction' },
  { id: 'features', label: 'Features' },
  { id: 'installation', label: 'Installation' },
  { id: 'usage', label: 'Usage' },
  { id: 'api', label: 'API Reference' },
];

export const Default: Story = {
  render: () => (
    <ScrollSpy>
      <div className="flex gap-8">
      <ScrollSpyNav className="sticky top-4 h-fit w-48">
        {sections.map((s) => (
          <ScrollSpyNavItem key={s.id} sectionId={s.id}>
            {s.label}
          </ScrollSpyNavItem>
        ))}
      </ScrollSpyNav>
      <div className="flex-1 space-y-8">
        {sections.map((s) => (
          <ScrollSpySection key={s.id} id={s.id} label={s.label}>
            <div className="rounded-lg border p-6">
              <h3 className="font-semibold text-lg">{s.label}</h3>
              <p className="mt-2 text-muted-foreground">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
                ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
                aliquip ex ea commodo consequat.
              </p>
              <p className="mt-4 text-muted-foreground">
                Duis aute irure dolor in reprehenderit in voluptate velit esse
                cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
                cupidatat non proident, sunt in culpa qui officia deserunt mollit
                anim id est laborum.
              </p>
            </div>
          </ScrollSpySection>
        ))}
      </div>
      </div>
    </ScrollSpy>
  ),
};
