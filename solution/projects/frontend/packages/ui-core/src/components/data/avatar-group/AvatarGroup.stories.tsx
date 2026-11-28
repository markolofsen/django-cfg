import type { Meta, StoryObj } from '@storybook/react-vite';
import { Avatar, AvatarGroup } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/AvatarGroup',
  component: AvatarGroup,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A group of avatars with stacking, overflow counting, and orientation support.',
      },
    },
  },
  argTypes: {
    orientation: { control: 'select', options: ['horizontal', 'vertical'] },
    dir: { control: 'select', options: ['ltr', 'rtl'] },
    size: { control: 'number' },
    max: { control: 'number' },
    reverse: { control: 'boolean' },
  },
} satisfies Meta<typeof AvatarGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

const avatars = [
  { src: 'https://i.pravatar.cc/150?u=1', fallback: 'AB' },
  { src: 'https://i.pravatar.cc/150?u=2', fallback: 'CD' },
  { src: 'https://i.pravatar.cc/150?u=3', fallback: 'EF' },
  { src: 'https://i.pravatar.cc/150?u=4', fallback: 'GH' },
  { src: 'https://i.pravatar.cc/150?u=5', fallback: 'IJ' },
];

export const Default: Story = {
  render: () => (
    <AvatarGroup>
      {avatars.map((a, i) => (
        <Avatar key={i}>
          <img src={a.src} alt={a.fallback} />
        </Avatar>
      ))}
    </AvatarGroup>
  ),
};

export const WithMax: Story = {
  render: () => (
    <AvatarGroup max={3}>
      {avatars.map((a, i) => (
        <Avatar key={i}>
          <img src={a.src} alt={a.fallback} />
        </Avatar>
      ))}
    </AvatarGroup>
  ),
};

export const Vertical: Story = {
  render: () => (
    <AvatarGroup orientation="vertical">
      {avatars.slice(0, 3).map((a, i) => (
        <Avatar key={i}>
          <img src={a.src} alt={a.fallback} />
        </Avatar>
      ))}
    </AvatarGroup>
  ),
};

export const CustomSize: Story = {
  render: () => (
    <AvatarGroup size={64}>
      {avatars.slice(0, 3).map((a, i) => (
        <Avatar key={i}>
          <img src={a.src} alt={a.fallback} />
        </Avatar>
      ))}
    </AvatarGroup>
  ),
};

export const Reversed: Story = {
  render: () => (
    <AvatarGroup reverse>
      {avatars.slice(0, 3).map((a, i) => (
        <Avatar key={i}>
          <img src={a.src} alt={a.fallback} />
        </Avatar>
      ))}
    </AvatarGroup>
  ),
};
