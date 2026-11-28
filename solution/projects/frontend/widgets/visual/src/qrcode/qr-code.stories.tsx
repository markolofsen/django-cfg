import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  QRCode,
  QRCodeCanvas,
  QRCodeSvg,
  QRCodeImage,
  QRCodeDownload,
  QRCodeOverlay,
  QRCodeSkeleton,
} from '.';

const meta = {
  title: 'Widgets/Visual/QRCode',
  component: QRCode,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A QR code generator with canvas, SVG, and image output formats.',
      },
    },
  },
  argTypes: {
    value: { control: 'text' },
    size: { control: 'number' },
    level: { control: 'select', options: ['L', 'M', 'Q', 'H'] },
    margin: { control: 'number' },
  },
  args: {
    value: 'https://djangocfg.dev',
  },
} satisfies Meta<typeof QRCode>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <QRCode value="https://djangocfg.dev" size={200}>
      <QRCodeCanvas />
      <QRCodeSkeleton />
    </QRCode>
  ),
};

export const Svg: Story = {
  render: () => (
    <QRCode value="https://djangocfg.dev" size={200}>
      <QRCodeSvg />
      <QRCodeSkeleton />
    </QRCode>
  ),
};

export const Image: Story = {
  render: () => (
    <QRCode value="https://djangocfg.dev" size={200}>
      <QRCodeImage />
      <QRCodeSkeleton />
    </QRCode>
  ),
};

export const WithOverlay: Story = {
  render: () => (
    <QRCode value="https://djangocfg.dev" size={200}>
      <QRCodeCanvas />
      <QRCodeOverlay className="size-10 rounded-full bg-white p-1">
        <span className="text-xs font-bold">DC</span>
      </QRCodeOverlay>
      <QRCodeSkeleton />
    </QRCode>
  ),
};

export const CustomColors: Story = {
  render: () => (
    <QRCode
      value="https://djangocfg.dev"
      size={200}
      foregroundColor="#3b82f6"
      backgroundColor="#f8fafc"
    >
      <QRCodeCanvas />
      <QRCodeSkeleton />
    </QRCode>
  ),
};

export const WithDownload: Story = {
  render: () => (
    <div className="flex flex-col items-center gap-4">
      <QRCode value="https://djangocfg.dev" size={200}>
        <QRCodeCanvas />
        <QRCodeSkeleton />
      </QRCode>
      <QRCodeDownload format="png" filename="djangocfg-qr">
        Download PNG
      </QRCodeDownload>
    </div>
  ),
};
