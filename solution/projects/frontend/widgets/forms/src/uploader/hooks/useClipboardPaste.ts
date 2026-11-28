'use client';

import { useEffect, useCallback, useRef, type RefObject } from 'react';
import { logger } from '../utils/logger';

export interface ClipboardPasteOptions {
  /** Whether paste is enabled */
  enabled?: boolean;
  /** Accept only these MIME type prefixes, e.g. ['image'] */
  acceptTypes?: string[];
  /** Max file size in bytes (optional) */
  maxBytes?: number;
  /** Called with resolved File objects from clipboard */
  onFiles: (files: File[]) => void;
  /** Called when paste happened but no suitable content found */
  onNoMatch?: () => void;
}

/**
 * Resolves clipboard data into File objects.
 *
 * Handles all real-world cases:
 *  1. Native file(s) copied from OS (e.g. Finder, Explorer)
 *  2. Screenshots (PrintScreen / Cmd+Shift+4) — come as image/png blob
 *  3. Images copied from browser ("Copy Image") — image/* blob
 *  4. Base64 data: URI in clipboard text  (data:image/png;base64,…)
 *  5. Remote image URL in clipboard text  (https://…/img.jpg)
 *  6. HTML with <img src="…"> — extracts first src and treats as case 4/5
 */
async function resolveClipboardFiles(
  e: ClipboardEvent,
  acceptTypes: string[],
  maxBytes: number | undefined,
): Promise<File[]> {
  const cd = e.clipboardData;
  if (!cd) return [];

  // ── 1 & 2 & 3: native files / blobs ─────────────────────────────────────
  const nativeFiles: File[] = [];
  for (const item of Array.from(cd.items)) {
    if (item.kind === 'file') {
      const file = item.getAsFile();
      if (!file) continue;
      if (!matchesAccept(file.type, acceptTypes)) continue;
      if (maxBytes && file.size > maxBytes) {
        logger.warn(`Clipboard file "${file.name}" exceeds size limit`);
        continue;
      }
      nativeFiles.push(file);
    }
  }
  if (nativeFiles.length > 0) return nativeFiles;

  // ── 4 & 5 & 6: text-based payloads ──────────────────────────────────────
  const text = cd.getData('text/plain').trim();
  const html = cd.getData('text/html').trim();

  // 6: extract src from HTML <img>
  const imgSrc = extractImgSrc(html);
  const source = imgSrc || text;

  if (!source) return [];

  // 4: base64 data URI
  if (source.startsWith('data:')) {
    const file = dataUriToFile(source);
    if (!file) return [];
    if (!matchesAccept(file.type, acceptTypes)) return [];
    if (maxBytes && file.size > maxBytes) {
      logger.warn('Pasted base64 image exceeds size limit');
      return [];
    }
    return [file];
  }

  // 5: remote URL
  if (/^https?:\/\//i.test(source)) {
    const mimeHint = guessMimeFromUrl(source);
    if (!matchesAccept(mimeHint, acceptTypes)) return [];
    try {
      const file = await fetchUrlAsFile(source);
      if (!file) return [];
      if (!matchesAccept(file.type, acceptTypes)) return [];
      if (maxBytes && file.size > maxBytes) {
        logger.warn('Pasted URL image exceeds size limit');
        return [];
      }
      return [file];
    } catch (err) {
      logger.warn('Failed to fetch pasted URL', {
        error: err instanceof Error ? err.message : String(err),
      });
      return [];
    }
  }

  return [];
}

// ── helpers ──────────────────────────────────────────────────────────────────

function matchesAccept(mimeType: string, acceptTypes: string[]): boolean {
  if (!acceptTypes.length) return true;
  return acceptTypes.some((accept) => {
    if (accept.endsWith('/*')) return mimeType.startsWith(accept.slice(0, -1));
    return mimeType === accept || mimeType.startsWith(accept + '/');
  });
}

function extractImgSrc(html: string): string | null {
  if (!html) return null;
  const match = html.match(/<img[^>]+src=["']([^"']+)["']/i);
  return match?.[1] ?? null;
}

function dataUriToFile(dataUri: string): File | null {
  try {
    const [header, base64] = dataUri.split(',');
    if (header === undefined || base64 === undefined) return null;
    const mimeMatch = header.match(/data:([^;]+)/);
    if (!mimeMatch) return null;
    const mime = mimeMatch[1];
    if (mime === undefined) return null;
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const ext = mime.split('/')[1]?.split('+')[0] ?? 'bin';
    return new File([bytes], `paste.${ext}`, { type: mime });
  } catch {
    return null;
  }
}

function guessMimeFromUrl(url: string): string {
  const ext = url.split('?')[0]?.split('.').pop()?.toLowerCase() ?? '';
  const map: Record<string, string> = {
    jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png',
    gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml',
    avif: 'image/avif', mp4: 'video/mp4', webm: 'video/webm',
    mp3: 'audio/mpeg', wav: 'audio/wav', pdf: 'application/pdf',
  };
  return map[ext] ?? 'application/octet-stream';
}

async function fetchUrlAsFile(url: string): Promise<File | null> {
  const resp = await fetch(url);
  if (!resp.ok) return null;
  const blob = await resp.blob();
  const ext = url.split('?')[0]?.split('.').pop()?.toLowerCase() ?? 'bin';
  const name = url.split('/').pop()?.split('?')[0] ?? `paste.${ext}`;
  return new File([blob], name, { type: blob.type || guessMimeFromUrl(url) });
}

// ── hook ─────────────────────────────────────────────────────────────────────

/**
 * Listens for paste events (Ctrl+V / Cmd+V) on the given element or
 * globally on `document` and resolves clipboard content into File objects.
 *
 * Supports: native files, screenshots, copied images, base64 URIs, remote URLs.
 */
export function useClipboardPaste(
  options: ClipboardPasteOptions,
  elementRef?: RefObject<HTMLElement | null>,
) {
  const {
    enabled = true,
    acceptTypes = ['image'],
    maxBytes,
    onFiles,
    onNoMatch,
  } = options;

  // Keep stable refs so we don't re-bind the listener on every render
  const onFilesRef = useRef(onFiles);
  const onNoMatchRef = useRef(onNoMatch);
  onFilesRef.current = onFiles;
  onNoMatchRef.current = onNoMatch;

  const handlePaste = useCallback(
    async (e: Event) => {
      const clipEvent = e as ClipboardEvent;
      const target = e.target as HTMLElement;
      const isTextTarget =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.isContentEditable;

      // If pasting into a text field/editor, only proceed if clipboard has a
      // file/blob but NO meaningful text — so we don't hijack mixed content
      // (e.g. Word copy which has both image and text in clipboard)
      if (isTextTarget) {
        const cd = clipEvent.clipboardData;
        if (!cd) return;
        const items = Array.from(cd.items);
        const hasFile = items.some((i) => i.kind === 'file');
        const hasText = cd.getData('text/plain').trim().length > 0;
        // Only intercept if there's a file and no accompanying text
        if (!hasFile || hasText) return;
      }

      const files = await resolveClipboardFiles(clipEvent, acceptTypes, maxBytes);
      if (files.length > 0) {
        e.preventDefault();
        onFilesRef.current(files);
      } else {
        onNoMatchRef.current?.();
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [acceptTypes.join(','), maxBytes],
  );

  useEffect(() => {
    if (!enabled) return;
    const target: EventTarget = elementRef?.current ?? document;
    target.addEventListener('paste', handlePaste);
    return () => target.removeEventListener('paste', handlePaste);
  }, [enabled, elementRef, handlePaste]);
}
