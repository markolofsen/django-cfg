'use client'

import { CTASection } from '@djangocfg/ui-nextjs/blocks'

export function CTASectionComponent() {
  return (
    <CTASection
      title="Ready to Build?"
      subtitle="Your production-ready Django backend is waiting. Start building your next great project."
      primaryCTA={{ label: "Open Admin Panel", href: "/private" }}
      secondaryCTA={{ label: "View Documentation", href: "https://djangocfg.com/docs" }}
    />
  )
}
