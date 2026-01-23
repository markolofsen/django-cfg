import { Code2, Palette, Shield, Sparkles, Zap } from 'lucide-react';

import { settings } from '@core/settings';
import { SuperHero } from '@djangocfg/ui-nextjs/blocks';
import { routes } from '@routes/index';

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
        href: routes.admin.overview.path
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
