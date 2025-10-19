/**
 * UILayout Types
 */

import { ReactNode } from 'react';

export interface ComponentCategory {
  id: string;
  label: string;
  icon: ReactNode;
  count?: number;
  description?: string;
}
