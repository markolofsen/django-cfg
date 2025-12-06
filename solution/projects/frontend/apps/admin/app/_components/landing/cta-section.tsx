'use client'

import { CTASection } from '@djangocfg/ui-nextjs/blocks'
import { routes } from '@routes/public'

export function CTASectionComponent() {
  return (
    <CTASection
      title="Ready to Launch Your MVP?"
      subtitle="Explore the demo to see what's possible. Build your AI-powered solution on a solid foundation."
      primaryCTA={{ label: "Try Admin Demo", href: routes.adminDemo.path }}
      secondaryCTA={{ label: "Private Area", href: routes.privateDemo.path }}
    />
  )
}
