import type { Metadata } from 'next';
import { JetBrains_Mono } from 'next/font/google';
import { BaseApp } from '@djangocfg/layouts';
import { CentrifugoProvider } from '@djangocfg/centrifugo';
import './globals.css';

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin', 'cyrillic'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Terminal',
  description: 'DjangoCFG Terminal',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const centrifugoUrl = process.env.NEXT_PUBLIC_CENTRIFUGO_URL || 'ws://localhost:8000/connection/websocket';

  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${jetbrainsMono.variable} font-mono antialiased bg-black text-white`}>
        <BaseApp theme={{ defaultTheme: 'dark' }}>
          <CentrifugoProvider url={centrifugoUrl}>
            {children}
          </CentrifugoProvider>
        </BaseApp>
      </body>
    </html>
  );
}
