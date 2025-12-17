import type { Metadata } from 'next';
import { generateMetadata } from '@core/metadata';

import { LandingView } from './LandingView';

export const metadata: Metadata = generateMetadata({
  title: 'Home',
  description: 'Welcome to Django CFG',
});

export default function LandingPage() {
  return <LandingView />;
}

