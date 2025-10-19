import Link from 'next/link';
import React from 'react';

import { Button } from '../components/button';
import { cn } from '../lib/utils';

interface CTAButton {
  label: string;
  href?: string;
  onClick?: () => void;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

interface CTASectionProps {
  title: string;
  subtitle?: string;
  primaryCTA?: CTAButton;
  secondaryCTA?: CTAButton;
  background?: 'default' | 'muted' | 'primary' | 'gradient';
  className?: string;
  children?: React.ReactNode;
}

export const CTASection: React.FC<CTASectionProps> = ({
  title,
  subtitle,
  primaryCTA,
  secondaryCTA,
  background = 'default',
  className,
  children
}) => {
  // Simple Tailwind 4 classes - no custom utilities
  const backgroundClasses = {
    default: 'bg-background',
    muted: 'bg-muted/30',
    primary: 'bg-primary/5',
    gradient: 'bg-gradient-to-b from-background via-primary/5 to-background',
  };

  return (
    <section
      className={cn(
        'relative py-16 sm:py-20 md:py-24 lg:py-32',
        backgroundClasses[background],
        className
      )}
    >
      {/* Simple decorative background - using only Tailwind classes */}
      {background === 'gradient' && (
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl aspect-square bg-primary/10 rounded-full blur-3xl" />
        </div>
      )}

      <div className="container max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-6 sm:space-y-8">
          {/* Title */}
          <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
            {title}
          </h2>

          {/* Subtitle */}
          {subtitle && (
            <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              {subtitle}
            </p>
          )}

          {/* CTA Buttons */}
          {(primaryCTA || secondaryCTA) && (
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center pt-4">
              {primaryCTA && (
                primaryCTA.onClick ? (
                  <Button
                    onClick={primaryCTA.onClick}
                    variant={primaryCTA.variant || 'default'}
                    size={primaryCTA.size || 'lg'}
                    className="w-full sm:w-auto"
                  >
                    {primaryCTA.label}
                  </Button>
                ) : (
                  <Button
                    asChild
                    variant={primaryCTA.variant || 'default'}
                    size={primaryCTA.size || 'lg'}
                    className="w-full sm:w-auto"
                  >
                    <Link href={primaryCTA.href || '#'}>
                      {primaryCTA.label}
                    </Link>
                  </Button>
                )
              )}

              {secondaryCTA && (
                secondaryCTA.onClick ? (
                  <Button
                    onClick={secondaryCTA.onClick}
                    variant={secondaryCTA.variant || 'outline'}
                    size={secondaryCTA.size || 'lg'}
                    className="w-full sm:w-auto"
                  >
                    {secondaryCTA.label}
                  </Button>
                ) : (
                  <Button
                    asChild
                    variant={secondaryCTA.variant || 'outline'}
                    size={secondaryCTA.size || 'lg'}
                    className="w-full sm:w-auto"
                  >
                    <Link href={secondaryCTA.href || '#'}>
                      {secondaryCTA.label}
                    </Link>
                  </Button>
                )
              )}
            </div>
          )}

          {/* Optional children content */}
          {children && (
            <div className="pt-8 sm:pt-12">
              {children}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
