import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { UploadDropzone } from '.';

/**
 * `UploadDropzone` in standalone mode (`uploadFn`) — no `UploadProvider`,
 * no rpldy. Drag/drop, click-to-pick, and Ctrl+V paste all funnel through
 * the same `handleFiles` → validation → `uploadFn` path. This is the
 * existing unified-input pattern the composer attach flow should reuse.
 */
const meta = {
  title: 'Widgets/Forms/Dropzone',
  component: UploadDropzone,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
} satisfies Meta<typeof UploadDropzone>;

export default meta;

type Story = StoryObj<typeof meta>;

function StandaloneDemo() {
  const [files, setFiles] = useState<string[]>([]);
  return (
    <div className="flex w-[480px] flex-col gap-3">
      <UploadDropzone
        accept={['image', 'video', 'document']}
        maxSizeMB={25}
        multiple
        pasteEnabled
        uploadFn={(picked) => {
          setFiles((prev) => [
            ...prev,
            ...picked.map((f) => `${f.name} (${(f.size / 1024).toFixed(1)} KB)`),
          ]);
        }}
        onPasteNoMatch={() => console.log('nothing pasteable')}
      />
      <div className="rounded-md border border-border bg-muted/30 p-3 text-xs">
        {files.length > 0 ? (
          <ul className="space-y-1">
            {files.map((f) => (
              <li key={f}>✓ {f}</li>
            ))}
          </ul>
        ) : (
          <span className="text-muted-foreground">
            Drop / click / paste — files appear here.
          </span>
        )}
      </div>
    </div>
  );
}

/** Standalone dropzone — drag, click, or Ctrl+V all hit one `uploadFn`. */
export const Standalone: Story = {
  render: () => <StandaloneDemo />,
};

/** Compact variant — denser dropzone for embedded contexts. */
export const Compact: Story = {
  render: () => (
    <div className="w-[420px]">
      <UploadDropzone
        accept={['image']}
        maxSizeMB={10}
        compact
        uploadFn={(picked) => console.log('picked', picked)}
      />
    </div>
  ),
};
