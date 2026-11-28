import type { Meta, StoryObj } from '@storybook/react-vite';
import { DownloadButton } from '@djangocfg/ui-core/components';

const meta: Meta<typeof DownloadButton> = {
  title: 'Packages/UI Core/Forms/DownloadButton',
  component: DownloadButton,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Button with built-in download flow, status icons (idle / downloading / success / error) and optional fetch-based transfer for auth headers and progress tracking.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof DownloadButton>;

export const Default: Story = {
  render: () => (
    <DownloadButton url="https://example.com/file.pdf" filename="document.pdf">
      Download PDF
    </DownloadButton>
  ),
};

export const WithProgress: Story = {
  render: () => (
    <DownloadButton
      url="https://example.com/large-file.zip"
      filename="archive.zip"
      useFetch
      showStatus
      onDownloadStart={() => {
         
        console.log('download start');
      }}
      onDownloadComplete={(name) => {
         
        console.log('download complete', name);
      }}
      onDownloadError={(err) => {
         
        console.error('download error', err);
      }}
    >
      Download archive
    </DownloadButton>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Uses fetch transport so download progress (status icons) can be reported through callbacks. Triggering against `example.com` will fail — that exercises the error icon path.',
      },
    },
  },
};

export const Loading: Story = {
  render: () => (
    <div className="flex flex-col gap-3">
      <DownloadButton url="https://httpbin.org/delay/10" filename="slow.bin" useFetch>
        Slow download (10s)
      </DownloadButton>
      <p className="text-sm text-muted-foreground">
        Click and observe the spinner icon while the request is in-flight.
      </p>
    </div>
  ),
};
