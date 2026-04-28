import { Code2, Palette, Shield, Sparkles, Zap } from 'lucide-react';
import Link from 'next/link';

import { settings } from '@core/settings';
import { Button } from '@djangocfg/ui-core';
import { routes } from '@routes/index';

const features = [
  { icon: <Code2 className="w-4 h-4" />, text: 'TypeScript' },
  { icon: <Zap className="w-4 h-4" />, text: 'SWR Hooks' },
  { icon: <Palette className="w-4 h-4" />, text: 'Dark Mode' },
  { icon: <Shield className="w-4 h-4" />, text: 'Responsive' },
];

const stats = [
  { number: '100%', label: 'Type Safe' },
  { number: 'Auto', label: 'Generated' },
  { number: 'Fast', label: 'Development' },
  { number: 'Modern', label: 'Stack' },
];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 via-background to-background py-16 md:py-24">
      <div className="container mx-auto px-4 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border bg-card px-4 py-1.5 text-sm font-medium text-primary mb-6">
          <Sparkles className="w-4 h-4" />
          Django + React Demo Platform
        </div>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
          Build Modern Apps{' '}
          <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
            with Django &amp; React
          </span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
          Full-stack demo showcasing Django REST API with auto-generated TypeScript clients,
          React hooks, and beautiful UI components. Perfect starting point for your next project.
        </p>
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          {features.map((f) => (
            <span
              key={f.text}
              className="inline-flex items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-sm"
            >
              {f.icon}
              {f.text}
            </span>
          ))}
        </div>
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          <Button asChild size="lg">
            <Link href={settings.links.docsUrl}>Documentation</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href={routes.admin.overview.path}>Demo Panel</Link>
          </Button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-3xl md:text-4xl font-bold">{s.number}</div>
              <div className="text-xs uppercase tracking-wider text-muted-foreground mt-1">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
