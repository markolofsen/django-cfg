/**
 * Component Configuration Types
 */

import React from 'react';

export interface ComponentConfig {
  name: string;
  category: string;
  description: string;
  importPath: string;
  example: string;
  preview: React.ReactNode;
}
