# Uploader

Drag-drop file uploader built on `@rpldy/uploady` with shadcn/ui styling.

## Installation

```bash
pnpm add @djangocfg/ui-tools
```

## Basic Usage

```tsx
import { Uploader } from '@djangocfg/ui-tools/upload';

function MyPage() {
  return (
    <Uploader
      destination="/api/upload"
      accept={['image', 'document']}
      maxSizeMB={10}
      onUploadComplete={(asset) => console.log('Uploaded:', asset)}
    />
  );
}
```

## Components

### Uploader

All-in-one component with dropzone and preview list.

```tsx
<Uploader
  destination="/api/upload"    // Upload URL
  accept={['image', 'video']}  // Asset types: image, audio, video, document
  maxSizeMB={50}               // Max file size
  multiple={true}              // Allow multiple files
  autoUpload={true}            // Auto-upload on drop
  showPreview={true}           // Show upload queue
  compact={false}              // Compact dropzone mode
  concurrent={3}               // Max concurrent uploads
  headers={{ 'X-Token': '...' }}
  params={{ folder: 'uploads' }}
  onUploadComplete={(asset, rawResponse) => {}}
  onUploadError={(error, file, rawResponse) => {}}
  onBatchComplete={(assets) => {}}
/>
```

### Standalone — custom upload handler (no UploadProvider)

If you handle uploads yourself (custom API hooks, multipart POST, etc.), pass `uploadFn` instead of wrapping with `UploadProvider`. Supports drag/drop, click, and Ctrl+V paste.

```tsx
import { UploadDropzone } from '@djangocfg/ui-tools/upload';

function MyUploader() {
  const { uploadAsset } = useAssets(); // your own API hook

  return (
    <UploadDropzone
      accept={['image', 'video']}
      maxSizeMB={50}
      pasteEnabled
      uploadFn={async (files) => {
        for (const file of files) {
          await uploadAsset({ file, name: file.name });
        }
      }}
    />
  );
}
```

### With Generated API Client (recommended for DjangoCFG apps)

When your project has a generated API client (from `generate_client`), use `UploadDropzone` with `uploadFn` that calls the generated mutation hook. Auth tokens are handled automatically by the API client — no manual headers needed.

```tsx
import { useCallback } from 'react';
import { UploadDropzone } from '@djangocfg/ui-tools/upload';

import { myApi } from '@/api/BaseClient';
import type { API } from '@/api/generated/my_app';
import { useCreateMyAppUploadCreate } from '@/api/generated/my_app/_utils/hooks';

const client = myApi as unknown as API;

function DocumentUploader({ projectSlug }: { projectSlug: string }) {
  const uploadMutation = useCreateMyAppUploadCreate();

  const handleUpload = useCallback(
    async (files: File[]) => {
      for (const file of files) {
        // Pass typed object — generated client builds FormData automatically
        await uploadMutation(projectSlug, { file, title: file.name }, client);
      }
    },
    [projectSlug, uploadMutation],
  );

  return (
    <UploadDropzone
      accept={['document']}
      maxSizeMB={50}
      multiple
      uploadFn={handleUpload}
    />
  );
}
```

**Why this pattern?**
- Generated client builds `FormData` from typed object (`{ file, title }`) — no manual `formData.append()`
- Auth token managed by API client — no `headers` prop, no localStorage access
- Same auth flow as all other API calls in the app
- Type-safe — generated hooks match Django serializers

> **Important:** Don't pass raw `FormData` to generated hooks. Pass a typed object matching the generated request interface (e.g. `{ file: File, title: string }`). The generated client handles `FormData` construction internally.

### Custom Composition (with rpldy)

```tsx
import {
  UploadProvider,
  UploadDropzone,
  UploadPreviewList,
  UploadAddButton,
  useUploadEvents,
} from '@djangocfg/ui-tools/upload';

function CustomUploader() {
  useUploadEvents({
    onFileComplete: (asset, rawResponse) => saveToState(asset),
    onError: (error, fileName, rawResponse) => toast.error(error),
  });

  return (
    <div className="grid grid-cols-2 gap-4">
      <UploadDropzone accept={['image']} />
      <UploadPreviewList />
    </div>
  );
}

<UploadProvider destination={{ url: '/api/upload' }}>
  <CustomUploader />
</UploadProvider>
```

### Page-Level Drop

Enable drag-drop anywhere on the page:

```tsx
<UploadProvider
  destination={{ url: '/api/upload' }}
  pageDropEnabled
  pageDropProps={{
    accept: ['image'],
    maxSizeMB: 10,
  }}
>
  <YourApp />
</UploadProvider>
```

Custom overlay:

```tsx
<UploadProvider
  destination={{ url: '/api/upload' }}
  pageDropEnabled
  pageDropOverlay={
    <div className="p-12 bg-primary/10 rounded-xl border-dashed border-2">
      <p className="text-xl">Drop files here!</p>
    </div>
  }
>
  <YourApp />
</UploadProvider>
```

## Exports

### Components

| Component | Needs UploadProvider | Description |
|-----------|---------------------|-------------|
| `Uploader` | Yes | All-in-one (Provider + Dropzone + Preview) |
| `UploadDropzone` | **Optional** | Drag-drop zone — use `uploadFn` for standalone mode |
| `UploadProvider` | — | Context provider wrapping @rpldy/uploady |
| `UploadPreviewList` | List of upload items with progress |
| `UploadPreviewItem` | Single item (thumbnail, status, actions) |
| `UploadAddButton` | Button to add files |
| `UploadPageDropOverlay` | Full-page drop overlay |

### Hooks

| Hook | Description |
|------|-------------|
| `useUploadEvents` | Subscribe to upload lifecycle events |
| `useUploadProvider` | Access uploady context |
| `useClipboardPaste` | Ctrl+V paste-to-upload (files, screenshots, base64, URLs) |
| `useAbortAll` | Abort all uploads |
| `useAbortBatch` | Abort batch by ID |
| `useAbortItem` | Abort single item |

### Utils

| Function | Description |
|----------|-------------|
| `getAssetTypeFromMime(mime)` | Get asset type from MIME |
| `buildAcceptString(types)` | Build accept string for input |
| `formatFileSize(bytes)` | Format bytes to human readable |
| `formatDuration(seconds)` | Format seconds to mm:ss |

### Types

```ts
type AssetType = 'image' | 'audio' | 'video' | 'document';

type UploadStatus = 'pending' | 'uploading' | 'complete' | 'error' | 'aborted';

interface UploadedAsset {
  id: string;
  name: string;
  type: AssetType;
  url: string;
  thumbnailUrl?: string;
  size: number;
  mimeType: string;
  duration?: number;
}

interface UploadItem {
  id: string;
  file: File;
  status: UploadStatus;
  progress: number;
  previewUrl?: string;
  asset?: UploadedAsset;
  error?: string;
}
```

## Server Response

Expected response format:

```json
{
  "id": "abc123",
  "url": "https://cdn.example.com/file.jpg",
  "thumbnail_url": "https://cdn.example.com/file_thumb.jpg",
  "duration": 120
}
```

Also supports: `uuid`, `file`, `file_url`, `thumbnail`, `thumb_url`, `preview_url`.

### Custom Response Handling

Use `onUploadComplete` callback to access raw response:

```tsx
<Uploader
  destination="/api/upload"
  onUploadComplete={(asset, rawResponse) => {
    // asset - parsed asset with defaults
    // rawResponse - original API response for custom handling
    console.log('Custom field:', rawResponse.my_custom_field);
  }}
  onUploadError={(error, file, rawResponse) => {
    // error - parsed error message
    // rawResponse - original error response for custom handling
  }}
/>
```

## Paste to Upload (Ctrl+V / Cmd+V)

Enable clipboard paste globally via the `pasteEnabled` prop. All cases are handled automatically:

| Clipboard content | What happens |
|-------------------|-------------|
| File(s) copied from OS | Upload directly |
| Screenshot (PrintScreen / Cmd+Shift+4) | Detected as `image/png`, uploaded |
| "Copy Image" from browser | Blob extracted and uploaded |
| `data:image/png;base64,…` in text | Decoded and uploaded as File |
| `https://…/photo.jpg` in text | Fetched and uploaded as File |
| `<img src="…">` in HTML clipboard | src extracted, treated as URL |
| Plain text, non-image URL | Ignored |

```tsx
// Simplest — enable on the all-in-one component
<Uploader
  destination="/api/upload"
  accept={['image']}
  pasteEnabled
  onPasteNoMatch={() => toast.info('Nothing to upload in clipboard')}
/>
```

```tsx
// Enable on UploadDropzone directly
<UploadDropzone
  accept={['image', 'video']}
  pasteEnabled
  onPasteNoMatch={() => console.log('no match')}
/>
```

```tsx
// Use the hook standalone for custom paste zones
import { useClipboardPaste } from '@djangocfg/ui-tools/upload';
import { useUploadProvider } from '@djangocfg/ui-tools/upload';

function MyCustomZone() {
  const { upload } = useUploadProvider();

  useClipboardPaste({
    enabled: true,
    acceptTypes: ['image', 'video'],  // MIME prefixes
    maxBytes: 10 * 1024 * 1024,       // 10 MB
    onFiles: (files) => upload(files),
    onNoMatch: () => console.log('nothing pasteable'),
  });

  return <div>Paste here (Ctrl+V)</div>;
}
```

> **Note:** Paste listeners skip `<input>`, `<textarea>`, and `contentEditable` elements
> so text editing is never interrupted.

## Features

- Drag & drop with visual feedback
- Paste to upload (Ctrl+V) — files, screenshots, images, base64, URLs
- Multiple file upload
- Concurrent uploads (configurable)
- Progress tracking per file
- Image preview thumbnails
- File type validation
- Size validation
- Abort/cancel uploads
- Page-level drop zone
- Tooltips for long filenames
- Error handling with retry
