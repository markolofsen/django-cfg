import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Moon, Sun, Volume2, VolumeX, Heart } from 'lucide-react';
import { Swap, SwapOff, SwapOn } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Effects/Swap',
  component: Swap,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A swap animation component that toggles between two states with various animations.',
      },
    },
  },
  argTypes: {
    animation: { control: 'select', options: ['fade', 'rotate', 'flip', 'scale'] },
    activationMode: { control: 'select', options: ['click', 'hover'] },
    disabled: { control: 'boolean' },
  },
} satisfies Meta<typeof Swap>;

export default meta;
type Story = StoryObj<typeof meta>;

function SwapHost(props: {
  animation?: 'fade' | 'rotate' | 'flip' | 'scale';
  activationMode?: 'click' | 'hover';
  disabled?: boolean;
}) {
  const [swapped, setSwapped] = useState(false);
  return (
    <Swap
      swapped={swapped}
      onSwappedChange={setSwapped}
      animation={props.animation}
      activationMode={props.activationMode}
      disabled={props.disabled}
      className="text-2xl"
    >
      <SwapOn>
        {/* eslint-disable-next-line no-restricted-syntax -- the colour IS the
            subject here, not a status: a sun is yellow and a moon is grey.
            A semantic token would retune them with the theme and say the
            wrong thing while doing it. */}
        <Sun className="size-8 text-yellow-500" />
      </SwapOn>
      <SwapOff>
        {/* eslint-disable-next-line no-restricted-syntax -- the colour IS the
            subject here, not a status: a sun is yellow and a moon is grey.
            A semantic token would retune them with the theme and say the
            wrong thing while doing it. */}
        <Moon className="size-8 text-slate-500" />
      </SwapOff>
    </Swap>
  );
}

export const Default: Story = {
  render: () => <SwapHost />,
};

export const Animations: Story = {
  render: () => (
    <div className="flex gap-8">
      <div className="flex flex-col items-center gap-2">
        <span className="text-xs text-muted-foreground">Fade</span>
        <SwapHost animation="fade" />
      </div>
      <div className="flex flex-col items-center gap-2">
        <span className="text-xs text-muted-foreground">Rotate</span>
        <SwapHost animation="rotate" />
      </div>
      <div className="flex flex-col items-center gap-2">
        <span className="text-xs text-muted-foreground">Flip</span>
        <SwapHost animation="flip" />
      </div>
      <div className="flex flex-col items-center gap-2">
        <span className="text-xs text-muted-foreground">Scale</span>
        <SwapHost animation="scale" />
      </div>
    </div>
  ),
};

export const HoverMode: Story = {
  render: () => (
    <SwapHost animation="fade" activationMode="hover" />
  ),
};

export const Disabled: Story = {
  render: () => (
    <SwapHost disabled />
  ),
};

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function VolumeToggleDemo() {
  const [swapped, setSwapped] = useState(false);
  return (
    <Swap
      swapped={swapped}
      onSwappedChange={setSwapped}
      animation="fade"
    >
      <SwapOn>
        {/* eslint-disable-next-line no-restricted-syntax -- decorative demo
            colour. These icons demonstrate the Swap animation, not a
            success/error state, so a status token would assert a meaning
            this story does not have. */}
        <Volume2 className="size-8 text-green-500" />
      </SwapOn>
      <SwapOff>
        {/* eslint-disable-next-line no-restricted-syntax -- decorative demo
            colour. These icons demonstrate the Swap animation, not a
            success/error state, so a status token would assert a meaning
            this story does not have. */}
        <VolumeX className="size-8 text-red-500" />
      </SwapOff>
    </Swap>
  );
}

export const VolumeToggle: Story = {
  render: () => <VolumeToggleDemo />,
};

function LikeButtonDemo() {
  const [swapped, setSwapped] = useState(false);
  return (
    <Swap
      swapped={swapped}
      onSwappedChange={setSwapped}
      animation="scale"
    >
      <SwapOn>
        {/* eslint-disable-next-line no-restricted-syntax -- decorative demo
            colour. These icons demonstrate the Swap animation, not a
            success/error state, so a status token would assert a meaning
            this story does not have. */}
        <Heart className="size-8 fill-red-500 text-red-500" />
      </SwapOn>
      <SwapOff>
        <Heart className="size-8 text-muted-foreground" />
      </SwapOff>
    </Swap>
  );
}

export const LikeButton: Story = {
  render: () => <LikeButtonDemo />,
};
