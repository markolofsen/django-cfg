import { ReactNode } from 'react';

import { PrivateLayout } from '@layouts/PrivateLayout';

export default function PrivateRouteLayout({ children }: { children: ReactNode }) {
  return <PrivateLayout>{children}</PrivateLayout>;
}
