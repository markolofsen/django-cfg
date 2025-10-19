/**
 * Blocks Configuration
 */

import React from 'react';
import {
  Hero,
  SuperHero,
  FeatureSection,
  CTASection,
  NewsletterSection,
  StatsSection,
  TestimonialSection,
} from '@djangocfg/ui/blocks';
import { Sparkles, BookOpen, Zap, Shield, Code } from 'lucide-react';
import type { ComponentConfig } from './types';

export const BLOCKS: ComponentConfig[] = [
  {
    name: 'Hero',
    category: 'blocks',
    description: 'Hero section with title, description, and CTAs',
    importPath: "import { Hero } from '@djangocfg/ui/blocks';",
    example: `<Hero
  title="Build Your Next Project"
  description="The best way to create modern web applications with React and TypeScript"
  primaryAction={{ label: "Get Started", href: "/docs" }}
  secondaryAction={{ label: "View Demo", href: "/demo" }}
/>`,
    preview: (
      <Hero
        title="Build Your Next Project"
        description="The best way to create modern web applications"
        primaryAction={{ label: "Get Started", href: "/docs" }}
        secondaryAction={{ label: "View Demo", href: "/demo" }}
      />
    ),
  },
  {
    name: 'SuperHero',
    category: 'blocks',
    description: 'Enhanced hero with badge, gradient title, features, and stats',
    importPath: "import { SuperHero } from '@djangocfg/ui/blocks';",
    example: `<SuperHero
  badge={{ icon: <Sparkles />, text: "New in v2.0" }}
  title="Next-Generation"
  titleGradient="Development Platform"
  subtitle="Build faster with our comprehensive UI library"
  features={[
    { icon: <span>⚛️</span>, text: "React 19" },
    { icon: <span>📘</span>, text: "TypeScript" },
    { icon: <span>🎨</span>, text: "Tailwind CSS 4" },
    { icon: <span>⚡</span>, text: "Lightning Fast" }
  ]}
  primaryAction={{ label: "Start Building", href: "/start" }}
  secondaryAction={{ label: "Learn More", href: "/docs", icon: <BookOpen /> }}
  stats={[
    { number: "56+", label: "Components" },
    { number: "7", label: "Blocks" },
    { number: "6", label: "Hooks" },
    { number: "100%", label: "Type Safe" }
  ]}
  scrollIndicator={false}
/>`,
    preview: (
      <SuperHero
        badge={{ icon: <Sparkles className="w-4 h-4" />, text: "New in v2.0" }}
        title="Next-Generation"
        titleGradient="Development Platform"
        subtitle="Build faster with our comprehensive UI library"
        features={[
          { icon: <span>⚛️</span>, text: "React 19" },
          { icon: <span>📘</span>, text: "TypeScript" },
          { icon: <span>🎨</span>, text: "Tailwind CSS 4" },
          { icon: <span>⚡</span>, text: "Lightning Fast" },
        ]}
        primaryAction={{ label: "Start Building", href: "/start" }}
        secondaryAction={{ label: "Learn More", href: "/docs", icon: <BookOpen /> }}
        stats={[
          { number: "56+", label: "Components" },
          { number: "7", label: "Blocks" },
          { number: "6", label: "Hooks" },
          { number: "100%", label: "Type Safe" },
        ]}
        scrollIndicator={false}
      />
    ),
  },
  {
    name: 'FeatureSection',
    category: 'blocks',
    description: 'Grid of features with icons and descriptions',
    importPath: "import { FeatureSection } from '@djangocfg/ui/blocks';",
    example: `<FeatureSection
  title="Everything You Need"
  subtitle="All the tools to build modern applications"
  features={[
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Lightning Fast",
      description: "Optimized for performance"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure",
      description: "Built with security in mind"
    }
  ]}
/>`,
    preview: (
      <FeatureSection
        title="Everything You Need"
        subtitle="All the tools to build modern applications"
        features={[
          {
            icon: <Zap className="w-6 h-6" />,
            title: "Lightning Fast",
            description: "Optimized for performance"
          },
          {
            icon: <Shield className="w-6 h-6" />,
            title: "Secure",
            description: "Built with security in mind"
          },
          {
            icon: <Code className="w-6 h-6" />,
            title: "Developer Friendly",
            description: "Great DX with TypeScript"
          }
        ]}
      />
    ),
  },
  {
    name: 'CTASection',
    category: 'blocks',
    description: 'Call-to-action section to drive conversions',
    importPath: "import { CTASection } from '@djangocfg/ui/blocks';",
    example: `<CTASection
  title="Ready to Get Started?"
  subtitle="Join thousands of developers building amazing products"
  primaryCTA={{ label: "Start Free Trial", href: "/signup" }}
  secondaryCTA={{ label: "Contact Sales", href: "/contact" }}
/>`,
    preview: (
      <CTASection
        title="Ready to Get Started?"
        subtitle="Join thousands of developers"
        primaryCTA={{ label: "Start Free Trial", href: "/signup" }}
        secondaryCTA={{ label: "Contact Sales", href: "/contact" }}
      />
    ),
  },
  {
    name: 'NewsletterSection',
    category: 'blocks',
    description: 'Email capture section for newsletters',
    importPath: "import { NewsletterSection } from '@djangocfg/ui/blocks';",
    example: `<NewsletterSection
  title="Stay Updated"
  description="Get the latest news delivered to your inbox"
  placeholder="Enter your email"
  buttonText="Subscribe"
  onSubmit={(email) => console.log(email)}
/>`,
    preview: (
      <NewsletterSection
        title="Stay Updated"
        description="Get the latest news delivered to your inbox"
        placeholder="Enter your email"
        buttonText="Subscribe"
        onSubmit={(email) => console.log('Subscribed:', email)}
      />
    ),
  },
  {
    name: 'StatsSection',
    category: 'blocks',
    description: 'Display key metrics and statistics',
    importPath: "import { StatsSection } from '@djangocfg/ui/blocks';",
    example: `<StatsSection
  title="Our Impact"
  stats={[
    { number: "10K+", label: "Active Users" },
    { number: "99.9%", label: "Uptime" }
  ]}
/>`,
    preview: (
      <StatsSection
        title="Our Impact"
        stats={[
          { number: "10K+", label: "Active Users" },
          { number: "500+", label: "Companies" },
          { number: "99.9%", label: "Uptime" },
          { number: "24/7", label: "Support" }
        ]}
      />
    ),
  },
  {
    name: 'TestimonialSection',
    category: 'blocks',
    description: 'Customer testimonials and reviews',
    importPath: "import { TestimonialSection } from '@djangocfg/ui/blocks';",
    example: `<TestimonialSection
  title="What Our Customers Say"
  testimonials={[{
    content: "This product changed how we work!",
    author: {
      name: "John Doe",
      title: "CEO",
      company: "Company"
    }
  }]}
/>`,
    preview: (
      <TestimonialSection
        title="What Our Customers Say"
        testimonials={[
          {
            content: "This product changed how we work. Highly recommended!",
            author: {
              name: "John Doe",
              title: "CEO",
              company: "Company",
              avatar: "/avatar.jpg"
            }
          }
        ]}
      />
    ),
  },
];
