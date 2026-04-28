'use client';

import { Bot, Layout, Rocket, Shield, Sparkles, Zap } from 'lucide-react';

const features = [
  {
    icon: <Bot className="w-6 h-6" />,
    title: 'AI Integration',
    description: 'Built-in support for LLMs, embeddings, and AI workflows. Ready for your AI features.',
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: 'Rapid Development',
    description: 'From idea to production in days, not months. Pre-built components and patterns.',
  },
  {
    icon: <Layout className="w-6 h-6" />,
    title: 'Modern Frontend',
    description: 'Next.js with TypeScript, Tailwind CSS, and shadcn/ui components.',
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: 'Secure by Default',
    description: 'JWT authentication, role-based access, and security best practices built-in.',
  },
  {
    icon: <Sparkles className="w-6 h-6" />,
    title: 'Type-Safe APIs',
    description: 'Auto-generated TypeScript clients from OpenAPI. No manual type definitions.',
  },
  {
    icon: <Rocket className="w-6 h-6" />,
    title: 'Production Ready',
    description: 'Docker, CI/CD, monitoring, and deployment scripts included.',
  },
];

export function FeaturesSection() {
  return (
    <section className="py-16 md:py-24 bg-card">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Built for Speed</h2>
          <p className="text-muted-foreground md:text-lg">
            Everything you need to launch your AI-powered MVP. Focus on your product, not infrastructure.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div key={f.title} className="rounded-xl border bg-background p-6">
              <div className="p-2 rounded-lg bg-primary/10 text-primary w-fit mb-3">{f.icon}</div>
              <h3 className="font-semibold mb-1.5">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
