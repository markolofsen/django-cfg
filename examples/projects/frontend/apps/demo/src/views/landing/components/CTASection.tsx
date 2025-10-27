import { ButtonLink, Card } from '@djangocfg/ui';
import { ArrowRight, Github } from 'lucide-react';
import { routes } from '@/core/routes';
import { settings } from '@/core/settings';
import Link from 'next/link';

export function CTASection() {
  return (
    <section className="py-20 lg:py-32">
      <div className="container mx-auto px-6">
        <Card className="max-w-4xl mx-auto overflow-hidden">
          <div className="relative p-12 lg:p-16">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-primary/5 to-transparent" />

            <div className="relative z-10 text-center space-y-8">
              <div className="space-y-4">
                <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight">
                  Ready to get started?
                </h2>
                <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
                  Explore the demo applications and see how easy it is to build modern full-stack apps
                  with Django and React.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <ButtonLink
                  href={routes.private.overview}
                  size="lg"
                  className="min-w-[200px] group"
                >
                  Start Exploring
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </ButtonLink>
                <ButtonLink
                  href={settings.links.githubUrl}
                  size="lg"
                  variant="outline"
                  className="min-w-[200px]"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="mr-2 h-4 w-4" />
                  View on GitHub
                </ButtonLink>
              </div>

              <div className="pt-8 text-sm text-muted-foreground">
                <p>Or check out the demo apps:</p>
                <div className="flex flex-wrap gap-4 justify-center mt-4">
                  <Link
                    href={routes.private.trading}
                    className="text-primary hover:underline font-medium"
                  >
                    Trading Platform
                  </Link>
                  <span className="text-muted-foreground/50">•</span>
                  <Link
                    href={routes.private.crypto}
                    className="text-primary hover:underline font-medium"
                  >
                    Crypto Dashboard
                  </Link>
                  <span className="text-muted-foreground/50">•</span>
                  <Link
                    href={routes.private.profile}
                    className="text-primary hover:underline font-medium"
                  >
                    User Profile
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
}
