import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';

import { ComposerAttachmentsView, type StagedAttachment } from '../../../chat/composer';

import '../../../styles/index.css';

const file = (id: string, name: string, size: number, kind: StagedAttachment['kind'], status: StagedAttachment['status']): StagedAttachment => ({ id, name, size, kind, status });
const done = (id: string, name: string, size: number, kind: StagedAttachment['kind'], mime: string, url = '#'): StagedAttachment =>
  file(id, name, size, kind, { state: 'done', attachment: { id, name, mime, size, kind, url } });
/** A small inline picture, so a thumbnail has something to show with no network. */
const PIC = (a: string, b: string) => `data:image/svg+xml;utf8,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='${a}'/><stop offset='1' stop-color='${b}'/></linearGradient></defs><rect width='40' height='40' fill='url(#g)'/></svg>`)}`;

const SCENES: ReadonlyArray<{ title: string; note: string; items: StagedAttachment[] }> = [
  { title: 'One file', note: 'A chip: icon, name, size, remove.', items: [done('1', 'weekly-summary.pdf', 188_416, 'document', 'application/pdf')] },
  {
    title: 'Pictures',
    note: 'A stored picture shows itself in place of the icon.',
    items: [done('1', 'IMG_7292.jpg', 397_312, 'image', 'image/jpeg', PIC('#6366f1', '#22d3ee')), done('2', 'screenshot-2026-11-09.png', 1_204_000, 'image', 'image/png', PIC('#f97316', '#facc15'))],
  },
  {
    title: 'Uploading',
    note: 'A bar along the chip’s edge: filled with progress, pulsing when the host reports none.',
    items: [file('1', 'export-march.csv', 4_200_000, 'text', { state: 'uploading', progress: 0.42 }), file('2', 'recording.m4a', 9_800_000, 'audio', { state: 'uploading', progress: undefined })],
  },
  {
    title: 'Many files',
    note: 'One row that scrolls sideways; it never grows taller.',
    items: Array.from({ length: 12 }, (_, i) => done(String(i), `report-${i + 1}.${i % 3 === 0 ? 'pdf' : i % 3 === 1 ? 'json' : 'md'}`, 12_000 * (i + 1), 'document', 'application/octet-stream')),
  },
  {
    title: 'One refused',
    note: 'The name and the reason on one line.',
    items: [file('1', 'video-2024-11-23.mp4', 48_000_000, 'video', { state: 'error', reason: 'type' })],
  },
  {
    title: 'Several refused',
    note: 'Folded into one line: the count and the reasons; the names are in the tooltip; one button clears them.',
    items: [
      file('1', 'video-2024-11-23.mp4', 48_000_000, 'video', { state: 'error', reason: 'type' }),
      file('2', '1-Контракт-и-деньги', 3_000, 'document', { state: 'error', reason: 'type' }),
      file('3', 'huge-archive.zip', 900_000_000, 'document', { state: 'error', reason: 'size' }),
      file('4', 'extra.pdf', 2_000, 'document', { state: 'error', reason: 'count' }),
      file('5', 'broken.txt', 1_000, 'text', { state: 'error', reason: 'upload', message: 'The server refused the upload' }),
    ],
  },
  {
    title: 'Everything at once',
    note: 'Accepted, uploading and refused together: the row on top, the one refused line under it.',
    items: [
      done('1', 'IMG_7292.jpg', 397_312, 'image', 'image/jpeg', PIC('#6366f1', '#22d3ee')),
      done('2', 'README.md', 777, 'text', 'text/markdown'),
      file('3', 'export-march.csv', 4_200_000, 'text', { state: 'uploading', progress: 0.7 }),
      file('4', 'video.mp4', 48_000_000, 'video', { state: 'error', reason: 'type' }),
      file('5', 'clip.mov', 48_000_000, 'video', { state: 'error', reason: 'type' }),
    ],
  },
];

function Scene({ title, note, items }: (typeof SCENES)[number]) {
  const [shown, setShown] = useState(items);
  return (
    <section className="space-y-1.5">
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="text-xs text-muted-foreground">{note}</p>
      <div className="rounded-xl border p-2">
        <ComposerAttachmentsView items={shown} onRemove={(id) => setShown((all) => all.filter((item) => item.id !== id))} />
        {shown.length === 0 ? <p className="px-1 py-0.5 text-xs text-muted-foreground">Empty: the tray draws nothing.</p> : null}
      </div>
    </section>
  );
}

function AllAttachments() {
  return <div className="space-y-5">{SCENES.map((scene) => <Scene key={scene.title} {...scene} />)}</div>;
}

/**
 * Every state of the composer's attachment tray on one page, at the width of the assistant column. The chips are live (remove works).
 * To see it in the real composer, use `Complete / Default` and attach files, or add one named `fail.txt` for an upload error.
 */
const meta = {
  title: 'Widgets/Chat/Assistant/Complete/Attachments',
  component: AllAttachments,
  parameters: { layout: 'padded' },
  decorators: [(Story) => <div className="mx-auto max-w-md"><Story /></div>],
} satisfies Meta<typeof AllAttachments>;
export default meta;
type Story = StoryObj<typeof meta>;

export const AllVariants: Story = {};
