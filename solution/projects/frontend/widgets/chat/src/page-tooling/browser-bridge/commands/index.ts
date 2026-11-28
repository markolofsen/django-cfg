'use client';

/**
 * Built-in bridge commands.
 *
 * Importing this module registers every command into the shared
 * registry (registration is a side effect of each command file). New
 * capabilities are added as a new file here, re-exported below.
 */

export { highlight, focus, clear } from './highlight';
export { scrollTo } from './scroll';
export { inspect } from './inspect';
export { fill, click } from './write';
export { sendMessage } from './chat';
