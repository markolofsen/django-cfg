/**
 * UI Guide App
 *
 * Complete UI Guide application with UILayout
 * Uses config-driven approach with context for navigation
 */

'use client';

import React from 'react';
import UIGuideView from './UIGuideView';

export function UIGuideApp() {
  // UIGuideView now includes UIGuideLanding as 'overview' category
  // and uses ShowcaseProvider context for navigation
  // All component data comes from centralized config
  return <UIGuideView />;
}
