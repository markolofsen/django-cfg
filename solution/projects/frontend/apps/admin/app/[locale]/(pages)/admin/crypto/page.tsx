import type { Metadata } from 'next';
import { generateMetadata } from '@core/metadata';

import { CryptoView } from './CryptoView';

export const metadata: Metadata = generateMetadata({
  title: 'Cryptocurrency',
  description: 'Explore coins, exchanges, and manage your wallets',
});

export default function CryptoPage() {
  return <CryptoView />;
}

