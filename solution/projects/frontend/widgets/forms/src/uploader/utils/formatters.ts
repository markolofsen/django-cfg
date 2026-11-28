/**
 * Middle-truncates a filename preserving the extension and a meaningful suffix.
 *
 * "telegram-cloud-photo-size-5-6152015652357607055-y.jpg"
 *   → "telegram-cloud-photo-…7055-y.jpg"  (maxLength=32)
 *
 * Short names are returned as-is.
 */
export function truncateFilename(filename: string, maxLength = 32): string {
  if (filename.length <= maxLength) return filename;

  const dotIdx = filename.lastIndexOf('.');
  const ext = dotIdx > 0 ? filename.slice(dotIdx) : '';          // ".jpg"
  const base = dotIdx > 0 ? filename.slice(0, dotIdx) : filename; // without ext

  // How many chars we can show from the start vs. end of the base
  const available = maxLength - ext.length - 1; // 1 for '…'
  if (available <= 2) return `…${ext}`;          // extreme edge case

  const headLen = Math.ceil(available * 0.55);
  const tailLen = available - headLen;

  const head = base.slice(0, headLen);
  const tail = tailLen > 0 ? base.slice(-tailLen) : '';

  return `${head}…${tail}${ext}`;
}

export function formatFileSize(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';

  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const k = 1024;
  // Clamp the unit index so absurdly large values never index out of bounds.
  const i = Math.min(
    Math.floor(Math.log(bytes) / Math.log(k)),
    units.length - 1,
  );
  const size = bytes / Math.pow(k, i);

  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
}

export function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
