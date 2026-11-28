/**
 * Copy text from a click handler. Returns whether it landed.
 *
 * The Clipboard API first. When it is refused — an embedded browser that
 * denies `clipboard-write`, a plain-http page, a document without focus — a
 * hidden textarea and `execCommand('copy')`, which those browsers still honour
 * within the same user gesture. Measured in the Claude desktop browser pane:
 * `writeText` rejects with "Write permission denied", the fallback succeeds.
 */
export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return copyWithTextarea(text);
  }
}

function copyWithTextarea(text: string): boolean {
  if (typeof document === 'undefined') return false;
  const area = document.createElement('textarea');
  area.value = text;
  area.setAttribute('readonly', '');
  area.style.position = 'fixed';
  area.style.opacity = '0';
  document.body.appendChild(area);
  area.select();
  try {
    return document.execCommand('copy');
  } catch {
    return false;
  } finally {
    area.remove();
  }
}
