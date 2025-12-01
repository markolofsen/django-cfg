import { Separator } from '@djangocfg/ui';
import { HeroSection, FeaturesSection, StatsSection, CTASection } from './components';

export function LandingView() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <HeroSection />

      <Separator className="container mx-auto" />

      {/* Features Section */}
      <FeaturesSection />

      <Separator className="container mx-auto" />

      {/* Stats Section */}
      <StatsSection />

      <Separator className="container mx-auto" />

      {/* CTA Section */}
      <CTASection />
    </div>
  );
}
