import { settings } from './_core';
import { ErrorLayout } from '@djangocfg/nextjs/errors';

export default function NotFound() {
  return <ErrorLayout code={404} supportEmail={settings.contact.email} />;
}

