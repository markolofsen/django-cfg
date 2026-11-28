/**
 * CST serialization — tree → deterministic JSON string.
 *
 * Key order is fixed so the same tree always produces the same string,
 * which makes the content hash (staleness detection) stable.
 */

import type {
  CSTContainerNode,
  CSTInteractiveNode,
  CSTNode,
  CSTRootNode,
  CSTTextNode,
} from './types';

/** Build a plain object with keys in a fixed order (undefined dropped). */
function ordered(entries: Array<[string, unknown]>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of entries) {
    if (value !== undefined) out[key] = value;
  }
  return out;
}

/** Normalize one node into a deterministic plain object. */
function normalizeNode(node: CSTNode): Record<string, unknown> {
  switch (node.type) {
    case 'root':
      return normalizeRoot(node);
    case 'interactive':
      return normalizeInteractive(node);
    case 'container':
      return normalizeContainer(node);
    case 'text':
      return normalizeText(node);
  }
}

function normalizeRoot(node: CSTRootNode): Record<string, unknown> {
  return ordered([
    ['type', node.type],
    ['title', node.title],
    ['url', node.url],
    ['children', node.children.map(normalizeNode)],
  ]);
}

function normalizeInteractive(
  node: CSTInteractiveNode,
): Record<string, unknown> {
  return ordered([
    ['type', node.type],
    ['role', node.role],
    ['ref', node.ref],
    ['name', node.name],
    ['value', node.value],
    ['placeholder', node.placeholder],
    ['disabled', node.disabled],
    ['checked', node.checked],
    ['expanded', node.expanded],
    ['required', node.required],
  ]);
}

function normalizeContainer(node: CSTContainerNode): Record<string, unknown> {
  return ordered([
    ['type', node.type],
    ['role', node.role],
    ['name', node.name],
    ['children', node.children.map(normalizeNode)],
  ]);
}

function normalizeText(node: CSTTextNode): Record<string, unknown> {
  return ordered([
    ['type', node.type],
    ['content', node.content],
  ]);
}

/** Serialize a CST tree to a deterministic JSON string. */
export function serializeCST(node: CSTNode): string {
  return JSON.stringify(normalizeNode(node));
}
