import type { Meta, StoryObj } from '@storybook/react-vite';
import { FileIcon, type FileIconSize } from '../FileIcon';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

/** A spread of file types that exercise the material-file-icons mapping. */
const SAMPLE_FILES = [
  'index.ts',
  'App.tsx',
  'styles.css',
  'theme.scss',
  'package.json',
  'README.md',
  'vite.config.ts',
  'tsconfig.json',
  '.gitignore',
  '.env',
  'Dockerfile',
  'main.py',
  'main.go',
  'lib.rs',
  'query.sql',
  'logo.svg',
  'photo.png',
  'sound.mp3',
  'movie.mp4',
  'archive.zip',
  'notes.pdf',
  'data.csv',
  'config.yaml',
  'unknown.xyzzy',
];

/** Conventional folder names that resolve to a dedicated icon. */
const SPECIAL_FOLDERS = [
  'src',
  'packages',
  'node_modules',
  'public',
  'assets',
  'dist',
  'docs',
  'tests',
  'scripts',
  'config',
  'components',
  'i18n',
  'db',
  '.git',
  '.github',
  '.vscode',
  'my-feature',
];

const SIZES: FileIconSize[] = [12, 14, 16, 20, 24, 32, 48, 64];

// ---------------------------------------------------------------------------
// Meta
// ---------------------------------------------------------------------------

const meta = {
  title: 'Widgets/Data/Tree/File icon',
  component: FileIcon,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  argTypes: {
    name: { control: 'text', description: 'File name (with extension) or folder name.' },
    isFolder: { control: 'boolean' },
    isExpanded: {
      control: 'boolean',
      description: 'Folder open / closed state. Ignored for files.',
    },
    size: {
      control: { type: 'inline-radio' },
      options: SIZES,
    },
    label: {
      control: 'text',
      description:
        'Accessible label. Empty = decorative (aria-hidden) — correct when a visible file name sits next to the icon.',
    },
  },
  args: {
    name: 'App.tsx',
    isFolder: false,
    isExpanded: false,
    size: 32,
    label: '',
  },
} satisfies Meta<typeof FileIcon>;

export default meta;

type Story = StoryObj<typeof meta>;

// ---------------------------------------------------------------------------
// Playground
// ---------------------------------------------------------------------------

export const Playground: Story = {
  render: ({ name, isFolder, isExpanded, size, label }) => (
    <FileIcon
      name={name}
      isFolder={isFolder}
      isExpanded={isExpanded}
      size={size}
      label={label || undefined}
    />
  ),
};

// ---------------------------------------------------------------------------
// Galleries
// ---------------------------------------------------------------------------

function IconCell({ children, caption }: { children: React.ReactNode; caption: string }) {
  return (
    <div className="flex w-24 flex-col items-center gap-1.5 rounded-md border bg-card p-3">
      {children}
      <span className="truncate text-[11px] text-muted-foreground" title={caption}>
        {caption}
      </span>
    </div>
  );
}

export const FileTypes: Story = {
  name: 'File types',
  render: () => (
    <div className="flex max-w-2xl flex-wrap gap-2">
      {SAMPLE_FILES.map((file) => (
        <IconCell key={file} caption={file}>
          <FileIcon name={file} size={32} />
        </IconCell>
      ))}
    </div>
  ),
};

export const Folders: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex max-w-2xl flex-wrap gap-2">
        {SPECIAL_FOLDERS.map((folder) => (
          <IconCell key={folder} caption={folder}>
            <FileIcon name={folder} isFolder size={32} />
          </IconCell>
        ))}
      </div>
      <p className="text-xs text-muted-foreground">
        Unknown folder names (e.g. <code>my-feature</code>) fall back to the generic
        folder icon, which respects the open / closed state.
      </p>
    </div>
  ),
};

export const FolderStates: Story = {
  name: 'Folder open / closed',
  render: () => (
    <div className="flex gap-2">
      <IconCell caption="closed">
        <FileIcon name="my-feature" isFolder size={32} />
      </IconCell>
      <IconCell caption="expanded">
        <FileIcon name="my-feature" isFolder isExpanded size={32} />
      </IconCell>
      <IconCell caption="src (special)">
        <FileIcon name="src" isFolder size={32} />
      </IconCell>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-wrap items-end gap-3">
      {SIZES.map((size) => (
        <div key={size} className="flex flex-col items-center gap-1.5">
          <FileIcon name="App.tsx" size={size} />
          <span className="text-[11px] text-muted-foreground">{size}px</span>
        </div>
      ))}
    </div>
  ),
};

export const Fallback: Story = {
  render: () => (
    <div className="flex flex-col gap-3">
      <div className="flex gap-2">
        <IconCell caption="no extension">
          <FileIcon name="LICENSE" size={32} />
        </IconCell>
        <IconCell caption="unknown ext">
          <FileIcon name="data.xyzzy" size={32} />
        </IconCell>
      </div>
      <p className="max-w-md text-xs text-muted-foreground">
        Unknown file types fall back to a neutral generic file icon. Icon SVGs
        are vendored statically (no runtime dependency), so resolution is
        synchronous and works in any bundler.
      </p>
    </div>
  ),
};

export const Accessible: Story = {
  name: 'Accessible label',
  render: () => (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2 text-sm">
        <FileIcon name="report.pdf" size={20} label="PDF document" />
        <span>Standalone icon with an explicit aria-label.</span>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <FileIcon name="report.pdf" size={20} />
        <span>report.pdf</span>
      </div>
      <p className="max-w-md text-xs text-muted-foreground">
        Next to a visible file name the icon is decorative (<code>aria-hidden</code>) —
        the default. Pass <code>label</code> only when the icon stands alone.
      </p>
    </div>
  ),
};
