'use client';

import { ContactPage } from '@djangocfg/ext-leads';
import { Section } from '@djangocfg/ui-nextjs';

export function ContactView() {
  return (
    <div className="min-h-screen bg-background">
      <Section className="py-16">
        <div className="container mx-auto px-4 max-w-6xl">
          <ContactPage />
        </div>
      </Section>
    </div>
  );
}
