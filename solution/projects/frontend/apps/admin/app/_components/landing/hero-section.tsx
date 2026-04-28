'use client';

import { Bot, Rocket, Sparkles, Zap } from 'lucide-react';
import Link from 'next/link';

import { Button } from '@djangocfg/ui-core';
import { routes } from '@routes/public';

const features = [
  { icon: <Bot className="w-4 h-4" />, text: 'AI Ready' },
  { icon: <Zap className="w-4 h-4" />, text: 'Fast Setup' },
  { icon: <Rocket className="w-4 h-4" />, text: 'Production' },
  { icon: <Sparkles className="w-4 h-4" />, text: 'Modern Stack' },
];

const stats = [
  { number: '10x', label: 'Faster Launch' },
  { number: '100%', label: 'Type Safe' },
  { number: 'AI', label: 'Native' },
];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 via-background to-background py-16 md:py-24">
      <div className="container mx-auto px-4 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border bg-card px-4 py-1.5 text-sm font-medium text-primary mb-6">
          <Sparkles className="w-4 h-4" />
          DjangoCFG Demo
        </div>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
          Build Your{' '}
          <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
            AI-Powered MVP
          </span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
          Launch your AI solution faster. Production-ready Django backend with modern Next.js
          frontend, type-safe APIs, and seamless AI integrations.
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
            <Link href={routes.adminDemo.path}>Try Admin Demo</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href={routes.privateDemo.path}>Private Area</Link>
          </Button>
        </div>
        <div className="grid grid-cols-3 gap-6 max-w-2xl mx-auto">
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
