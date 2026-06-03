import type { ReactNode } from 'react';

import { PublicLayout } from '@layouts/PublicLayout';

/** Public marketing shell (navbar + footer) for legal pages. */
export default function LegalRouteLayout({ children }: { children: ReactNode }) {
  return <PublicLayout>{children}</PublicLayout>;
}
