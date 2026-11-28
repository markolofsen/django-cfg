'use client';

import React, { memo } from 'react';
import { Mail } from 'lucide-react';

/**
 * WebmailIcon — brand glyph for a webmail provider.
 *
 * lucide-react dropped brand icons, so the recognisable providers get a small
 * inline SVG (brand-coloured, currentColor-agnostic). Everything else falls
 * back to a generic `Mail` glyph that inherits `currentColor`.
 *
 * `provider` is the slug from the backend WebmailLink (gmail, outlook, …).
 */
export interface WebmailIconProps {
  provider: string;
  className?: string;
  size?: number;
}

const SIZE = 20;

function GmailGlyph({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M2 6.5A1.5 1.5 0 0 1 3.5 5H4l8 6 8-6h.5A1.5 1.5 0 0 1 22 6.5V18a1 1 0 0 1-1 1h-2V9.2l-7 5.2-7-5.2V19H3a1 1 0 0 1-1-1V6.5Z" />
      <path fill="#EA4335" d="M2 6.5A1.5 1.5 0 0 1 3.5 5H4l8 6-2 1.5L2 6.5Z" />
      <path fill="#FBBC04" d="M22 6.5A1.5 1.5 0 0 0 20.5 5H20l-8 6 2 1.5 8-6Z" />
      <path fill="#34A853" d="M3 19h2V9.2L3 7.7V19Zm18 0h-2V9.2l2-1.5V19Z" />
    </svg>
  );
}

function OutlookGlyph({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <rect x="10" y="5" width="12" height="14" rx="1" fill="#0A2767" />
      <rect x="10" y="5" width="12" height="7" fill="#0364B8" />
      <path fill="#28A8EA" d="M22 8.5 13 13l9 4.5V8.5Z" />
      <rect x="2" y="6" width="11" height="12" rx="2" fill="#0078D4" />
      <path fill="#fff" d="M7.5 8.6c-2 0-3.2 1.5-3.2 3.5s1.2 3.4 3.1 3.4 3.2-1.4 3.2-3.5-1.2-3.4-3.1-3.4Zm0 1.5c1 0 1.5.9 1.5 1.9s-.5 2-1.5 2-1.5-1-1.5-2 .5-1.9 1.5-1.9Z" />
    </svg>
  );
}

function YandexGlyph({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="10" fill="#FC3F1D" />
      <path fill="#fff" d="M13 6h-1.8c-2 0-3.3 1.3-3.3 3.2 0 1.5.7 2.4 2 3.3L7.6 18h1.9l2.2-4.9h.6V18H14V6Zm-.7 5.7c-1.1 0-1.6-.6-1.6-2 0-1.5.6-2.1 1.6-2.1h.7v4.1h-.7Z" />
    </svg>
  );
}

function MailRuGlyph({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="10" fill="#005FF9" />
      <path fill="#fff" d="M12 7.2a4.8 4.8 0 1 0 3 8.6l-1-1.2a3.2 3.2 0 1 1 1.1-2.6h1.6a4.8 4.8 0 0 0-4.7-4.8Zm0 3.2a1.6 1.6 0 1 0 0 3.2 1.6 1.6 0 0 0 0-3.2Z" />
      <path fill="#FFA930" d="M16.8 12v.9a1.4 1.4 0 0 0 2.6.7A5 5 0 1 0 12 17v-1.6a3.4 3.4 0 1 1 3.2-4.6h1.6Z" />
    </svg>
  );
}

const GLYPHS: Record<string, React.FC<{ size: number }>> = {
  gmail: GmailGlyph,
  outlook: OutlookGlyph,
  yandex: YandexGlyph,
  mail_ru: MailRuGlyph,
};

function WebmailIconRaw({ provider, className, size = SIZE }: WebmailIconProps) {
  const Glyph = GLYPHS[provider];
  if (Glyph) {
    return (
      <span className={className} style={{ display: 'inline-flex', lineHeight: 0 }}>
        <Glyph size={size} />
      </span>
    );
  }
  return <Mail className={className} width={size} height={size} aria-hidden="true" />;
}

export const WebmailIcon = memo(WebmailIconRaw);
