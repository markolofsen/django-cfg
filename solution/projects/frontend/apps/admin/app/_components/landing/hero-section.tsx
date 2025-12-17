'use client'

import { Bot, Rocket, Sparkles, Zap } from 'lucide-react';

import { SuperHero } from '@djangocfg/ui-nextjs/blocks';
import { routes } from '@routes/public';

export function HeroSection() {
  return (
    <SuperHero
      badge={{ icon: <Sparkles className="w-4 h-4" />, text: "DjangoCFG Demo" }}
      title="Build Your"
      titleGradient="AI-Powered MVP"
      subtitle="Launch your AI solution faster. Production-ready Django backend with modern Next.js frontend, type-safe APIs, and seamless AI integrations."
      features={[
        { icon: <Bot className="w-4 h-4" />, text: "AI Ready" },
        { icon: <Zap className="w-4 h-4" />, text: "Fast Setup" },
        { icon: <Rocket className="w-4 h-4" />, text: "Production" },
        { icon: <Sparkles className="w-4 h-4" />, text: "Modern Stack" }
      ]}
      primaryAction={{ label: "Try Admin Demo", href: routes.adminDemo.path }}
      secondaryAction={{ label: "Private Area", href: routes.privateDemo.path }}
      stats={[
        { number: "10x", label: "Faster Launch" },
        { number: "100%", label: "Type Safe" },
        { number: "AI", label: "Native" }
      ]}
      backgroundVariant="mesh-gradient"
      backgroundIntensity="medium"
    />
  )
}
