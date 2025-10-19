/**
 * UI Guide Landing Page
 *
 * Beautiful landing page for Django CFG UI Library
 * Uses ready blocks from @djangocfg/ui/blocks
 */

'use client';

import React from 'react';
import {
  Package,
  Sparkles,
  Zap,
  Shield,
  Palette,
  Code2,
  Blocks,
  Github,
  BookOpen,
} from 'lucide-react';
import {
  SuperHero,
  FeatureSection,
  StatsSection,
  CTASection,
} from '@djangocfg/ui/blocks';
import { useShowcase } from './context';

interface UIGuideLandingProps {
  githubUrl?: string;
}

export function UIGuideLanding({
  githubUrl = 'https://github.com'
}: UIGuideLandingProps) {
  const { setCurrentCategory } = useShowcase();

  const handleBrowseComponents = () => {
    setCurrentCategory('forms');
  };

  const handleViewBlocks = () => {
    setCurrentCategory('blocks');
  };
  return (
    <div className="min-h-screen">
      {/* Hero Section using SuperHero block */}
      <SuperHero
        badge={{
          icon: <Sparkles className="w-4 h-4" />,
          text: "56+ Components · 7 Blocks · 11 Hooks"
        }}
        title="Django CFG"
        titleGradient="UI Library"
        subtitle="Modern React component library built with Next.js 15, Radix UI, and Tailwind CSS 4"
        features={[
          { icon: <span>⚛️</span>, text: "React 19" },
          { icon: <span>📘</span>, text: "TypeScript" },
          { icon: <span>🎨</span>, text: "Tailwind CSS 4" },
          { icon: <span>🌙</span>, text: "Dark Mode" },
        ]}
        primaryAction={{
          label: "Explore Components",
          onClick: handleBrowseComponents
        }}
        secondaryAction={{
          label: "View Blocks",
          onClick: handleViewBlocks,
          icon: <BookOpen className="w-5 h-5" />
        }}
        stats={[
          { number: "56+", label: "Components" },
          { number: "7", label: "Blocks" },
          { number: "11", label: "Hooks" },
          { number: "100%", label: "Type Safe" },
        ]}
      />

      {/* Features Section using FeatureSection block */}
      <FeatureSection
        title="Everything You Need"
        subtitle="A comprehensive component library with all the building blocks for modern web applications"
        columns={3}
        background="card"
        features={[
          {
            icon: <Package className="w-6 h-6" />,
            title: "56+ Components",
            description: "From basic buttons to complex data tables, we've got you covered with production-ready components",
          },
          {
            icon: <Blocks className="w-6 h-6" />,
            title: "Landing Page Blocks",
            description: "Pre-built sections like Hero, Features, CTA, Testimonials to ship landing pages faster",
          },
          {
            icon: <Zap className="w-6 h-6" />,
            title: "Lightning Fast",
            description: "Optimized for performance with React 19 and Next.js 15 for blazing fast user experiences",
          },
          {
            icon: <Shield className="w-6 h-6" />,
            title: "Fully Accessible",
            description: "Built on Radix UI primitives ensuring WCAG compliance and keyboard navigation support",
          },
          {
            icon: <Palette className="w-6 h-6" />,
            title: "Themeable",
            description: "Dark mode built-in with CSS variables. Customize colors, spacing, and typography easily",
          },
          {
            icon: <Code2 className="w-6 h-6" />,
            title: "TypeScript First",
            description: "Fully typed with TypeScript for better DX, autocomplete, and fewer runtime errors",
          },
        ]}
      />

      {/* Stats Section using StatsSection block */}
      <StatsSection
        title="Built for Scale"
        subtitle="Everything you need to build modern web applications"
        columns={4}
        stats={[
          {
            number: "56+",
            label: "UI Components",
            description: "Production-ready",
          },
          {
            number: "7",
            label: "Landing Blocks",
            description: "Pre-built sections",
          },
          {
            number: "11",
            label: "React Hooks",
            description: "Custom utilities",
          },
          {
            number: "100%",
            label: "Type Safe",
            description: "Full TypeScript",
          },
        ]}
      />

      {/* CTA Section using CTASection block */}
      <CTASection
        title="Ready to Build Something Amazing?"
        subtitle="Start exploring our component library and ship your next project faster with pre-built, accessible components"
        primaryCTA={{
          label: "Browse Components",
          onClick: handleBrowseComponents
        }}
        secondaryCTA={{
          label: "View Blocks",
          onClick: handleViewBlocks
        }}
        background="gradient"
      />

      {/* Simple Footer */}
      <footer className="border-t py-8 sm:py-10 md:py-12 bg-background">
        <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Package className="w-4 h-4" />
              <span>Built with Radix UI + Tailwind CSS</span>
            </div>
            <div className="flex items-center gap-6">
              <button
                onClick={handleBrowseComponents}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Components
              </button>
              <button
                onClick={handleViewBlocks}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Blocks
              </button>
              <button
                onClick={() => window.open(githubUrl, '_blank')}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
              >
                <Github className="w-4 h-4" />
                GitHub
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
