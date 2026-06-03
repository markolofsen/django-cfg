import type { ReactNode } from 'react';

import { PrivateLayout } from '@layouts/PrivateLayout';

/**
 * Private shell for `/private/*` (sidebar + header). Providers live once in
 * `[locale]/layout.tsx`.
 */
export default function PrivateRouteLayout({ children }: { children: ReactNode }) {
  return <PrivateLayout>{children}</PrivateLayout>;
}
