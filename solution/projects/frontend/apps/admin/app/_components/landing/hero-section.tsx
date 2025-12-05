'use client'

import { SuperHero } from '@djangocfg/ui-nextjs/blocks'
import { Sparkles, Zap, Shield, Database } from 'lucide-react'

export function HeroSection() {
  return (
    <SuperHero
      badge={{ icon: <Sparkles className="w-4 h-4" />, text: "Django-CFG" }}
      title="Your New"
      titleGradient="Project is Ready"
      subtitle="Production-ready Django backend with Next.js admin. Type-safe configuration, modern UI, and AI-native documentation out of the box."
      codeCommand="django-cfg create-project my_app"
      features={[
        { icon: <Database className="w-4 h-4" />, text: "PostgreSQL" },
        { icon: <Zap className="w-4 h-4" />, text: "Redis" },
        { icon: <Shield className="w-4 h-4" />, text: "JWT Auth" },
        { icon: <Sparkles className="w-4 h-4" />, text: "AI-Native" }
      ]}
      primaryAction={{ label: "Open Admin", href: "/private" }}
      secondaryAction={{ label: "API Docs", href: "/api/docs" }}
      stats={[
        { number: "8+", label: "Built-in Apps" },
        { number: "100%", label: "Type Safe" },
        { number: "30s", label: "Setup Time" }
      ]}
      backgroundVariant="mesh-gradient"
      backgroundIntensity="medium"
    />
  )
}
