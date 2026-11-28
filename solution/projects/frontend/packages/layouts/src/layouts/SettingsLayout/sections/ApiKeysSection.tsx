'use client';

import React from 'react';

import { ApiKeySection } from '../components/ApiKeySection';

/**
 * Built-in "API keys" section body. Wraps the existing ApiKeySection (display,
 * regenerate, test). The panel header supplies the title.
 */
export const ApiKeysSection: React.FC = () => (
  <div className="mx-auto max-w-2xl space-y-6">
    <ApiKeySection />
  </div>
);
