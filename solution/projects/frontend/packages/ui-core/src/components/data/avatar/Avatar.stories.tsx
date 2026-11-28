import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Avatar',
  component: Avatar,
  tags: ['autodocs'],
} satisfies Meta<typeof Avatar>;

export default meta;

type Story = StoryObj<typeof meta>;

const AVATARS = [
  { src: 'https://github.com/shadcn.png', fallback: 'CN' },
  { src: 'https://github.com/vercel.png', fallback: 'VC' },
  { src: 'https://github.com/radix-ui.png', fallback: 'RX' },
];

export const Image: Story = {
  render: () => (
    <Avatar>
      <AvatarImage src="https://github.com/markolofsen.png" alt="markolofsen" />
      <AvatarFallback>MK</AvatarFallback>
    </Avatar>
  ),
};

export const Fallback: Story = {
  render: () => (
    <Avatar>
      <AvatarImage src="/broken-image.jpg" alt="User" />
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      {['h-6 w-6', 'h-8 w-8', 'h-10 w-10', 'h-14 w-14', 'h-20 w-20'].map(
        (cls) => (
          <Avatar key={cls} className={cls}>
            <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
        ),
      )}
    </div>
  ),
};

export const Group: Story = {
  render: () => (
    <div className="flex -space-x-4">
      {AVATARS.map((a, i) => (
        <Avatar key={i} className="border-2 border-background">
          <AvatarImage src={a.src} />
          <AvatarFallback>{a.fallback}</AvatarFallback>
        </Avatar>
      ))}
      <Avatar className="border-2 border-background">
        <AvatarFallback>+5</AvatarFallback>
      </Avatar>
    </div>
  ),
};

export const WithStatus: Story = {
  render: () => (
    <div className="flex gap-4">
      {[
        // Presence is a status, so it reads from the status tokens: a theme that
        // retunes "success" retunes the online dot with it.
        { src: 'https://github.com/shadcn.png', fb: 'CN', color: 'bg-success' },
        { src: 'https://github.com/vercel.png', fb: 'VC', color: 'bg-warning' },
        { src: 'https://github.com/radix-ui.png', fb: 'RX', color: 'bg-muted-foreground' },
      ].map((a, i) => (
        <div key={i} className="relative">
          <Avatar>
            <AvatarImage src={a.src} />
            <AvatarFallback>{a.fb}</AvatarFallback>
          </Avatar>
          <span
            className={`absolute bottom-0 right-0 h-3 w-3 rounded-full ${a.color} border-2 border-background`}
          />
        </div>
      ))}
    </div>
  ),
};
