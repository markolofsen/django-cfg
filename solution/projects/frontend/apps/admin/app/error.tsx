'use client';

import { useEffect } from 'react';

import { settings } from '@core/settings';
import { ErrorLayout } from '@djangocfg/layouts/components';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Error:', error);
  }, [error]);

  return <ErrorLayout code={500} supportEmail={settings.contact.email} />;
}

