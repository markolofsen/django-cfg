import type { Meta, StoryObj } from '@storybook/react-vite';
import { Button } from '@djangocfg/ui-core/components';
import {
  Tour,
  TourPopover,
  TourSpotlight,
  useTourContext,
} from '.';

const meta = {
  title: 'Widgets/Overlay/Tour',
  component: Tour,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'Guided product tour with steps and popovers. `<Tour>` is uncontrolled — open it ' +
          'with `defaultOpen` or imperatively via `useTourContext().open()`. ' +
          'There is no controlled `open` prop; binding external state to `defaultOpen` is a no-op ' +
          'after the first render.',
      },
    },
  },
  args: {
    steps: [],
    children: null,
  },
} satisfies Meta<typeof Tour>;

export default meta;
type Story = StoryObj<typeof meta>;

const steps = [
  {
    id: 'step1',
    target: '#tour-header',
    title: 'Welcome',
    description: 'This is the header area of the application.',
    placement: 'bottom' as const,
  },
  {
    id: 'step2',
    target: '#tour-sidebar',
    title: 'Navigation',
    description: 'Use the sidebar to navigate between sections.',
    placement: 'right' as const,
  },
  {
    id: 'step3',
    target: '#tour-content',
    title: 'Main Content',
    description: 'Your main workspace appears here.',
    placement: 'top' as const,
  },
];

// Lives *inside* <Tour> so it can call useTourContext().open() —
// the only way to (re)start a tour from outside state.
function StartTourButton() {
  const { open } = useTourContext();
  return (
    <Button onClick={open} size="sm">
      Start tour
    </Button>
  );
}

function TourScaffold({ defaultOpen = false }: { defaultOpen?: boolean }) {
  return (
    <Tour steps={steps} defaultOpen={defaultOpen}>
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between gap-4">
          <div
            id="tour-header"
            className="flex-1 rounded-lg border border-border bg-muted/50 p-4 text-center text-sm font-medium"
          >
            Header
          </div>
          <StartTourButton />
        </div>
        <div className="flex gap-4">
          <div
            id="tour-sidebar"
            className="w-32 rounded-lg border border-border bg-muted/50 p-4 text-center text-sm font-medium"
          >
            Sidebar
          </div>
          <div
            id="tour-content"
            className="flex-1 rounded-lg border border-border bg-muted/50 p-8 text-center text-sm font-medium"
          >
            Main Content
          </div>
        </div>
      </div>
      <TourSpotlight />
      <TourPopover />
    </Tour>
  );
}

/** Click **Start tour** in the header to open the tour at step 1. */
export const Default: Story = {
  render: () => <TourScaffold />,
};

/** `defaultOpen` — tour opens immediately on mount. */
export const OpenByDefault: Story = {
  render: () => <TourScaffold defaultOpen />,
};
