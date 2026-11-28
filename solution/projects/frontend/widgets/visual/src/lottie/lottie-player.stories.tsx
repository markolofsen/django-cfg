import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyLottiePlayer as LottiePlayer } from './lazy';

// Public CC0 Lottie animations (stable hosts).
const ANIMATIONS = {
  loadingDots: 'https://assets1.lottiefiles.com/packages/lf20_iv4dsx3q.json',
  successCheck:
    'https://lottie.host/4db68bbd-31f6-4cd8-84eb-189de081159a/IGmMCqhzpt.json',
  rocket: 'https://assets3.lottiefiles.com/packages/lf20_x62chJ.json',
} as const;

const DEFAULT_SRC = ANIMATIONS.rocket;

const meta = {
  title: 'Widgets/Visual/Lottie',
  component: LottiePlayer,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  argTypes: {
    src: {
      control: 'select',
      options: Object.values(ANIMATIONS),
      table: { category: 'Source' },
      description: 'Animation JSON URL or inline data object.',
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl', 'full'],
      table: { category: 'Layout' },
    },
    autoplay: {
      control: 'boolean',
      table: { category: 'Playback', defaultValue: { summary: 'true' } },
    },
    loop: {
      control: 'boolean',
      table: { category: 'Playback', defaultValue: { summary: 'true' } },
    },
    speed: {
      control: { type: 'select' },
      options: [0.5, 1, 1.5, 2],
      table: { category: 'Playback', defaultValue: { summary: '1' } },
    },
    direction: {
      control: { type: 'inline-radio' },
      options: [1, -1],
      table: { category: 'Playback', defaultValue: { summary: '1' } },
    },
    controls: {
      control: 'boolean',
      table: { category: 'UI', defaultValue: { summary: 'false' } },
    },
    background: {
      control: 'color',
      table: { category: 'UI' },
    },
    showLoading: {
      control: 'boolean',
      table: { category: 'UI', defaultValue: { summary: 'true' } },
    },
  },
  args: {
    src: DEFAULT_SRC,
    size: 'md',
    autoplay: true,
    loop: true,
    speed: 1,
    direction: 1,
    controls: false,
    showLoading: true,
  },
  render: (args) => (
    <div className="h-64 w-64">
      <LottiePlayer {...args} />
    </div>
  ),
} satisfies Meta<typeof LottiePlayer>;

export default meta;

type Story = StoryObj<typeof meta>;

// -----------------------------------------------------------------------------
// Playground — all controls wired up
// -----------------------------------------------------------------------------

export const Playground: Story = {};

// -----------------------------------------------------------------------------
// Curated presets
// -----------------------------------------------------------------------------

export const FromUrl: Story = {
  args: {
    src: ANIMATIONS.loadingDots,
    autoplay: true,
    loop: true,
  },
};

export const Paused: Story = {
  args: {
    src: ANIMATIONS.rocket,
    autoplay: false,
    controls: true,
  },
};

export const Slow: Story = {
  args: {
    src: ANIMATIONS.rocket,
    speed: 0.5,
    loop: true,
  },
};

export const Fast: Story = {
  args: {
    src: ANIMATIONS.rocket,
    speed: 2,
    loop: true,
  },
};

export const Reverse: Story = {
  args: {
    src: ANIMATIONS.rocket,
    direction: -1,
    loop: true,
  },
};

export const Looped: Story = {
  args: {
    src: ANIMATIONS.successCheck,
    loop: true,
    autoplay: true,
  },
};

// -----------------------------------------------------------------------------
// Interactive controls — play/pause, loop toggle, speed cycle
// -----------------------------------------------------------------------------

export const InteractiveControls: Story = {
  args: {
    src: ANIMATIONS.rocket,
    controls: true,
    autoplay: true,
  },
};

// -----------------------------------------------------------------------------
// Hover to play — animation runs only while the pointer is over it
// -----------------------------------------------------------------------------

export const HoverToPlay: Story = {
  args: {
    src: ANIMATIONS.rocket,
    hoverToPlay: true,
    autoplay: false,
  },
};

// -----------------------------------------------------------------------------
// Error state — invalid URL surfaces a retryable error
// -----------------------------------------------------------------------------

export const ErrorState: Story = {
  args: {
    src: 'https://lottie.host/this-animation-does-not-exist.json',
  },
};
