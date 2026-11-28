'use client';

/**
 * ImageViewer Debug Logger
 *
 * Uses universal logger with media-specific helpers.
 * Logs go to both console (dev) and zustand store (for Console panel).
 */

import { createMediaLogger } from '@djangocfg/ui-core/lib';

export const imageDebug = createMediaLogger('ImageViewer');

export default imageDebug;
