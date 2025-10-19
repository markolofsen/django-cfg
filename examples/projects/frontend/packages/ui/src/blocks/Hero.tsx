import Link from 'next/link';
import React from 'react';

import { Button } from '../components/button';
import { cn } from '../lib/utils';

interface HeroProps {
  title: string;
  subtitle?: string;
  description?: string;
  primaryAction?: {
    label: string;
    href: string;
    variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  };
  secondaryAction?: {
    label: string;
    href: string;
    variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  };
  background?: 'gradient' | 'solid' | 'image' | 'dark';
  className?: string;
  children?: React.ReactNode;
}

export const Hero: React.FC<HeroProps> = ({
  title,
  subtitle,
  description,
  primaryAction,
  secondaryAction,
  background = 'dark',
  className,
  children
}) => {
  // Simple Tailwind 4 classes only - no custom utilities
  const backgroundClasses = {
    gradient: 'bg-gradient-to-b from-primary/10 to-background',
    solid: 'bg-primary text-primary-foreground',
    image: 'bg-cover bg-center bg-no-repeat text-white',
    dark: 'bg-background text-foreground',
  };

  return (
    <section className={cn(
      'relative py-16 sm:py-20 md:py-24 lg:py-32',
      backgroundClasses[background],
      className
    )}>
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto">
          {subtitle && (
            <p className="text-base sm:text-lg md:text-xl mb-4 sm:mb-6 text-muted-foreground font-medium">
              {subtitle}
            </p>
          )}

          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6 sm:mb-8 leading-tight">
            {title}
          </h1>

          {description && (
            <p className="text-lg sm:text-xl md:text-2xl mb-8 sm:mb-10 md:mb-12 text-muted-foreground leading-relaxed max-w-3xl mx-auto">
              {description}
            </p>
          )}

          {(primaryAction || secondaryAction) && (
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
              {primaryAction && (
                <Button
                  asChild
                  variant={primaryAction.variant || 'default'}
                  size="lg"
                  className="w-full sm:w-auto"
                >
                  <Link href={primaryAction.href}>
                    {primaryAction.label}
                  </Link>
                </Button>
              )}

              {secondaryAction && (
                <Button
                  asChild
                  variant={secondaryAction.variant || 'outline'}
                  size="lg"
                  className="w-full sm:w-auto"
                >
                  <Link href={secondaryAction.href}>
                    {secondaryAction.label}
                  </Link>
                </Button>
              )}
            </div>
          )}

          {children && (
            <div className="mt-12 sm:mt-14 md:mt-16 flex justify-center">
              {children}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}; 