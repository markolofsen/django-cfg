/**
 * Sanitization utilities for Mermaid diagrams
 * @module Mermaid/builders/core/sanitize
 */

/**
 * Characters that need to be escaped or removed in Mermaid labels
 */
const UNSAFE_CHARS = /["\n\r\\<>{}|]/g;

/**
 * Mermaid reserved keywords that cannot be used as node IDs.
 *
 * Stored LOWERCASE because the lookup lowercases its input. Held as `classDef`
 * and `linkStyle`, those two never matched — a node called `classDef` emitted a
 * style directive where a node was meant, and what followed was read as its
 * arguments.
 */
const RESERVED_WORDS = new Set([
  'end',
  'graph',
  'subgraph',
  'direction',
  'click',
  'style',
  'class',
  'classdef',
  'linkstyle',
  'callback',
]);

/**
 * Sanitize a label for use in Mermaid diagrams
 * Removes or escapes characters that could break the diagram syntax
 */
export function sanitizeLabel(label: string): string {
  return label
    .replace(UNSAFE_CHARS, '')
    .replace(/&/g, '&amp;')
    .replace(/'/g, "'")
    .trim();
}

/**
 * Convert an ID to a valid Mermaid node ID
 * - Removes special characters
 * - Adds optional prefix to ensure uniqueness
 * - Ensures ID starts with a letter
 * - Escapes reserved Mermaid keywords
 */
export function toNodeId(id: string, prefix = ''): string {
  // Remove special characters and spaces
  const cleanId = id.replace(/[^a-zA-Z0-9_]/g, '_');

  // Ensure starts with letter
  let safeId = /^[a-zA-Z]/.test(cleanId) ? cleanId : `n${cleanId}`;

  // Escape reserved words by adding underscore suffix
  if (RESERVED_WORDS.has(safeId.toLowerCase())) {
    safeId = `${safeId}_`;
  }

  return prefix ? `${prefix}_${safeId}` : safeId;
}

/**
 * Escape a string for use in quoted Mermaid labels
 */
export function escapeQuoted(str: string): string {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '<br/>');
}

/**
 * Format a label with optional subtitle using HTML-like syntax
 */
export function formatLabel(main: string, subtitle?: string): string {
  const sanitized = sanitizeLabel(main);
  if (!subtitle) return sanitized;
  return `${sanitized}<br/><small>${sanitizeLabel(subtitle)}</small>`;
}
