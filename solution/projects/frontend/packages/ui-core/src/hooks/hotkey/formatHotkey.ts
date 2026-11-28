'use client';

/**
 * Human-readable hotkey formatter.
 *
 * Translates a `react-hotkeys-hook` combo string into the glyphs users
 * expect to see in tooltips and cheat-sheets. Honours macOS conventions
 * (⌘ ⌃ ⌥ ⇧) on Apple devices and falls back to text labels elsewhere.
 *
 * @example
 * formatHotkey('mod+k')     // → '⌘K' on Mac, 'Ctrl+K' elsewhere
 * formatHotkey('shift+/')   // → '⇧/'
 * formatHotkey('escape')    // → 'Esc'
 * formatHotkey('g t')       // → 'G then T' (chord)
 */
export function formatHotkey(combo: string, opts: { mac?: boolean } = {}): string {
  const mac = opts.mac ?? detectMac();

  // Chord: tokens separated by spaces.
  if (combo.includes(' ')) {
    return combo
      .split(/\s+/)
      .map((part) => formatHotkey(part, { mac }))
      .join(' then ');
  }

  // Multiple alternatives via comma — show the first.
  if (combo.includes(',')) {
    const first = combo.split(',')[0]?.trim();
    return first ? formatHotkey(first, { mac }) : combo;
  }

  return combo
    .split('+')
    .map((token) => token.trim().toLowerCase())
    .filter(Boolean)
    .map((token) => formatToken(token, mac))
    .join(mac ? '' : '+');
}

function detectMac(): boolean {
  if (typeof navigator === 'undefined') return false;
  // navigator.userAgentData is Chromium-only; fall back to platform sniff.
  const ua = (navigator.userAgent || '').toLowerCase();
  const platform = (navigator.platform || '').toLowerCase();
  return /mac|iphone|ipad|ipod/.test(platform) || /mac os|macintosh/.test(ua);
}

function formatToken(token: string, mac: boolean): string {
  switch (token) {
    case 'mod':
      return mac ? '⌘' : 'Ctrl';
    case 'meta':
    case 'cmd':
    case 'command':
      return mac ? '⌘' : 'Win';
    case 'ctrl':
    case 'control':
      return mac ? '⌃' : 'Ctrl';
    case 'alt':
    case 'option':
      return mac ? '⌥' : 'Alt';
    case 'shift':
      return mac ? '⇧' : 'Shift';
    case 'escape':
    case 'esc':
      return 'Esc';
    case 'enter':
    case 'return':
      return mac ? '⏎' : 'Enter';
    case 'tab':
      return mac ? '⇥' : 'Tab';
    case 'space':
      return mac ? 'Space' : 'Space';
    case 'backspace':
      return mac ? '⌫' : 'Backspace';
    case 'delete':
    case 'del':
      return mac ? '⌦' : 'Del';
    case 'arrowup':
    case 'up':
      return '↑';
    case 'arrowdown':
    case 'down':
      return '↓';
    case 'arrowleft':
    case 'left':
      return '←';
    case 'arrowright':
    case 'right':
      return '→';
    default:
      if (token.length === 1) return token.toUpperCase();
      return token.charAt(0).toUpperCase() + token.slice(1);
  }
}
