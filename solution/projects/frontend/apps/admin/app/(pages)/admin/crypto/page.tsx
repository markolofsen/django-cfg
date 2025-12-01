import type { Metadata } from 'next';
import { CryptoView } from './CryptoView';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Cryptocurrency',
  description: 'Explore coins, exchanges, and manage your wallets',
});

export default function CryptoPage() {
  return <CryptoView />;
}

