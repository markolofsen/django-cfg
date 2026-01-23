import type { Metadata } from 'next';
import { generateMetadata } from '@core/metadata';

import { TradingView } from './TradingView';

export const metadata: Metadata = generateMetadata({
  title: 'Trading',
  description: 'Manage your trading portfolio and orders',
});

export default function TradingPage() {
  return <TradingView />;
}

