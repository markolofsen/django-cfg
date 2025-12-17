'use client'

import { Bot, Layout, Rocket, Shield, Sparkles, Zap } from 'lucide-react';

import { FeatureSection } from '@djangocfg/ui-nextjs/blocks';

const features = [
  {
    icon: <Bot className="w-6 h-6" />,
    title: "AI Integration",
    description: "Built-in support for LLMs, embeddings, and AI workflows. Ready for your AI features."
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: "Rapid Development",
    description: "From idea to production in days, not months. Pre-built components and patterns."
  },
  {
    icon: <Layout className="w-6 h-6" />,
    title: "Modern Frontend",
    description: "Next.js with TypeScript, Tailwind CSS, and shadcn/ui components."
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: "Secure by Default",
    description: "JWT authentication, role-based access, and security best practices built-in."
  },
  {
    icon: <Sparkles className="w-6 h-6" />,
    title: "Type-Safe APIs",
    description: "Auto-generated TypeScript clients from OpenAPI. No manual type definitions."
  },
  {
    icon: <Rocket className="w-6 h-6" />,
    title: "Production Ready",
    description: "Docker, CI/CD, monitoring, and deployment scripts included."
  }
]

export function FeaturesSection() {
  return (
    <FeatureSection
      title="Built for Speed"
      subtitle="Everything you need to launch your AI-powered MVP. Focus on your product, not infrastructure."
      features={features}
    />
  )
}
