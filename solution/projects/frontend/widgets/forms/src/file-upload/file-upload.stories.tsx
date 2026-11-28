import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { X } from 'lucide-react';
import {
  FileUpload,
  FileUploadDropzone,
  FileUploadList,
  FileUploadItem,
  FileUploadItemPreview,
  FileUploadItemMetadata,
  FileUploadItemProgress,
  FileUploadItemDelete,
  FileUploadClear,
} from '.';

const meta = {
  title: 'Widgets/Forms/FileUpload',
  component: FileUpload,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A file upload component with drag-and-drop, preview, progress, and validation.',
      },
    },
  },
} satisfies Meta<typeof FileUpload>;

export default meta;
type Story = StoryObj<typeof meta>;

function FileUploadHost(props: {
  multiple?: boolean;
  maxFiles?: number;
  accept?: string;
  maxSize?: number;
}) {
  const [files, setFiles] = useState<File[]>([]);
  return (
    <div className="w-96 space-y-4">
      <FileUpload
        value={files}
        onValueChange={setFiles}
        multiple={props.multiple}
        maxFiles={props.maxFiles}
        accept={props.accept}
        maxSize={props.maxSize}
      >
        <FileUploadDropzone className="h-40">
          <div className="flex flex-col items-center gap-2 text-sm text-muted-foreground">
            <span>Drag & drop files here</span>
            <span>or click to browse</span>
          </div>
        </FileUploadDropzone>
        <FileUploadList>
          {files.map((file) => (
            <FileUploadItem key={file.name} value={file}>
              <FileUploadItemPreview />
              <FileUploadItemMetadata />
              <FileUploadItemProgress />
              <FileUploadItemDelete>
                <X className="h-4 w-4" />
              </FileUploadItemDelete>
            </FileUploadItem>
          ))}
        </FileUploadList>
        {files.length > 0 && (
          <FileUploadClear className="text-sm text-destructive hover:underline">
            Clear all
          </FileUploadClear>
        )}
      </FileUpload>
    </div>
  );
}

export const Default: Story = {
  render: () => <FileUploadHost multiple />,
};

export const SingleFile: Story = {
  render: () => <FileUploadHost />,
};

export const ImagesOnly: Story = {
  render: () => <FileUploadHost multiple accept="image/*" maxSize={5 * 1024 * 1024} />,
};

export const MaxThreeFiles: Story = {
  render: () => <FileUploadHost multiple maxFiles={3} />,
};
