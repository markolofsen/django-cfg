import type { Metadata } from 'next';
import { LandingView } from './LandingView';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Home',
  description: 'Welcome to Django CFG',
});

export default function LandingPage() {
  return <LandingView />;
}

