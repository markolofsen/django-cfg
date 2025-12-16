/**
 * Offline Fallback Page
 *
 * Shown when user is offline and page is not cached
 */

import type { Metadata } from 'next';
import { WifiOff } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Offline',
  description: 'You are currently offline',
};

export default function OfflinePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
      <WifiOff className="w-16 h-16 mb-6 text-muted-foreground" />

      <h1 className="text-3xl font-bold mb-2">You're Offline</h1>

      <p className="text-muted-foreground mb-8 max-w-md">
        Please check your internet connection and try again.
      </p>

      <button
        onClick={() => window.location.reload()}
        className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        Try Again
      </button>
    </div>
  );
}
