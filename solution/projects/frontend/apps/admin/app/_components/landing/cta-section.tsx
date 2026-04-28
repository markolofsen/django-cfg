'use client';

import Link from 'next/link';

import { Button } from '@djangocfg/ui-core';
import { routes } from '@routes/public';

export function CTASectionComponent() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 to-background py-16 md:py-20">
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Launch Your MVP?</h2>
          <p className="text-muted-foreground md:text-lg mb-8">
            Explore the demo to see what&apos;s possible. Build your AI-powered solution on a solid foundation.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Button asChild size="lg">
              <Link href={routes.adminDemo.path}>Try Admin Demo</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href={routes.privateDemo.path}>Private Area</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
