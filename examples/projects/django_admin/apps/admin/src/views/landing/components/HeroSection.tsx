import { SuperHero } from '@djangocfg/ui/blocks';
import { Sparkles, Code2, Zap, Shield, Palette } from 'lucide-react';
import { routes } from '@/core/routes';
import { settings } from '@/core';

export function HeroSection() {
  return (
    <SuperHero
      badge={{
        icon: <Sparkles className="w-4 h-4" />,
        text: "Django + React Demo Platform"
      }}
      title="Build Modern Apps"
      titleGradient="with Django & React"
      subtitle="Full-stack demo showcasing Django REST API with auto-generated TypeScript clients, React hooks, and beautiful UI components. Perfect starting point for your next project."
      features={[
        {
          icon: <Code2 className="w-4 h-4" />,
          text: "TypeScript"
        },
        {
          icon: <Zap className="w-4 h-4" />,
          text: "SWR Hooks"
        },
        {
          icon: <Palette className="w-4 h-4" />,
          text: "Dark Mode"
        },
        {
          icon: <Shield className="w-4 h-4" />,
          text: "Responsive"
        }
      ]}
      primaryAction={{
        label: "Documentation",
        href: settings.links.docsUrl
      }}
      secondaryAction={{
        label: "Demo Panel",
        href: routes.public.demo.path
      }}
      stats={[
        { number: "100%", label: "Type Safe" },
        { number: "Auto", label: "Generated" },
        { number: "Fast", label: "Development" },
        { number: "Modern", label: "Stack" }
      ]}
      backgroundVariant="waves"
      showBackgroundSwitcher={true}
    />
  );
}
