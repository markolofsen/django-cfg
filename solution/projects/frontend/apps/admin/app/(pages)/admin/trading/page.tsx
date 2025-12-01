import type { Metadata } from 'next';
import { TradingView } from './TradingView';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Trading',
  description: 'Manage your trading portfolio and orders',
});

export default function TradingPage() {
  return <TradingView />;
}

