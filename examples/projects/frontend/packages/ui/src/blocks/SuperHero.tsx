import { ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';
import React from 'react';

import { cn } from '../lib/utils';

interface HeroFeature {
  icon: React.ReactNode;
  text: string;
}

interface StatItem {
  number: string;
  label: string;
  icon?: React.ReactNode;
}

interface SuperHeroProps {
  badge?: {
    icon?: React.ReactNode;
    text: string;
  };
  title: string;
  titleGradient?: string;
  subtitle: string;
  features?: HeroFeature[];
  primaryAction?: {
    label: string;
    href?: string;
    onClick?: () => void;
  };
  secondaryAction?: {
    label: string;
    href?: string;
    onClick?: () => void;
    icon?: React.ReactNode;
  };
  stats?: StatItem[];
  floatingElements?: React.ReactNode;
  scrollIndicator?: boolean;
  className?: string;
}

export const SuperHero: React.FC<SuperHeroProps> = ({
  badge,
  title,
  titleGradient,
  subtitle,
  features = [],
  primaryAction,
  secondaryAction,
  stats = [],
  floatingElements,
  scrollIndicator = true,
  className
}) => {
  return (
    <section className={cn(
      "relative overflow-hidden bg-gradient-to-br from-background via-primary/10 to-secondary/20",
      className
    )}>
      {/* Animated Background Elements - Smooth Mesh Gradient Effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Large morphing blobs */}
        <div
          className="absolute -top-20 -right-20 w-96 h-96 bg-gradient-to-br from-primary/20 via-primary/10 to-transparent blur-3xl"
          style={{ animation: 'float 20s ease-in-out infinite, morph 15s ease-in-out infinite' }}
        ></div>
        <div
          className="absolute -bottom-20 -left-20 w-96 h-96 bg-gradient-to-tr from-secondary/20 via-secondary/10 to-transparent blur-3xl"
          style={{ animation: 'float 25s ease-in-out infinite reverse, morph 18s ease-in-out infinite 2s' }}
        ></div>

        {/* Medium floating orbs */}
        <div
          className="absolute top-1/4 right-1/3 w-64 h-64 bg-gradient-to-bl from-primary/15 to-transparent blur-2xl rounded-full"
          style={{ animation: 'float-diagonal 22s ease-in-out infinite' }}
        ></div>
        <div
          className="absolute bottom-1/3 left-1/4 w-72 h-72 bg-gradient-to-tr from-secondary/15 to-transparent blur-2xl rounded-full"
          style={{ animation: 'float-diagonal 24s ease-in-out infinite reverse 5s' }}
        ></div>

        {/* Small accent orbs */}
        <div
          className="absolute top-1/2 left-1/2 w-40 h-40 bg-primary/10 rounded-full blur-xl"
          style={{ animation: 'float-x 18s ease-in-out infinite' }}
        ></div>
        <div
          className="absolute top-1/3 right-1/4 w-32 h-32 bg-secondary/10 rounded-full blur-xl"
          style={{ animation: 'float-slow 25s ease-in-out infinite 3s' }}
        ></div>

        {/* Gradient overlay for depth */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/5 to-background/20"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-24 lg:py-32 relative z-0">
        <div className="text-center">
          {/* Enhanced Badge */}
          {badge && (
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-medium mb-6 border border-primary/20 hover:bg-primary/20 transition-all duration-300">
              {badge.icon || <Sparkles className="w-4 h-4" />}
              {badge.text}
            </div>
          )}

          {/* Enhanced Main Title */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-foreground mb-6 leading-tight">
            {title.split('\n').map((line, index) => (
              <React.Fragment key={index}>
                {line}
                {index < title.split('\n').length - 1 && <br />}
              </React.Fragment>
            ))}
            {titleGradient && (
              <>
                <br />
                <span className="bg-gradient-to-r from-primary via-primary/80 to-secondary bg-clip-text text-transparent animate-pulse">
                  {titleGradient}
                </span>
              </>
            )}
          </h1>

          {/* Enhanced Subtitle */}
          <p className="text-xl sm:text-2xl lg:text-3xl text-muted-foreground mb-8 max-w-4xl mx-auto leading-relaxed">
            {subtitle}
          </p>

          {/* Enhanced Features */}
          {features.length > 0 && (
            <div className="flex flex-wrap justify-center gap-6 mb-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 text-sm text-muted-foreground bg-card/50 px-4 py-2 rounded-full border border-border/50 hover:border-primary/30 hover:bg-card transition-all duration-300"
                >
                  {feature.icon}
                  <span>{feature.text}</span>
                </div>
              ))}
            </div>
          )}

          {/* Enhanced CTA Buttons */}
          {(primaryAction || secondaryAction) && (
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              {primaryAction && (
                primaryAction.onClick ? (
                  <button
                    onClick={primaryAction.onClick}
                    className="group inline-flex items-center justify-center px-8 py-4 bg-primary text-primary-foreground rounded-sm font-semibold text-lg hover:bg-primary/90 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
                  >
                    {primaryAction.label}
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                  </button>
                ) : (
                  <Link
                    href={primaryAction.href || '#'}
                    className="group inline-flex items-center justify-center px-8 py-4 bg-primary text-primary-foreground rounded-sm font-semibold text-lg hover:bg-primary/90 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
                  >
                    {primaryAction.label}
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                  </Link>
                )
              )}
              {secondaryAction && (
                secondaryAction.onClick ? (
                  <button
                    onClick={secondaryAction.onClick}
                    className="group inline-flex items-center justify-center px-8 py-4 border border-border text-foreground rounded-sm font-semibold text-lg hover:bg-muted/50 transition-all duration-300 hover:scale-105 hover:border-primary/30"
                  >
                    {secondaryAction.label}
                    {secondaryAction.icon && (
                      <span className="ml-2 w-5 h-5 group-hover:rotate-12 transition-transform duration-300">
                        {secondaryAction.icon}
                      </span>
                    )}
                  </button>
                ) : (
                  <Link
                    href={secondaryAction.href || '#'}
                    className="group inline-flex items-center justify-center px-8 py-4 border border-border text-foreground rounded-sm font-semibold text-lg hover:bg-muted/50 transition-all duration-300 hover:scale-105 hover:border-primary/30"
                  >
                    {secondaryAction.label}
                    {secondaryAction.icon && (
                      <span className="ml-2 w-5 h-5 group-hover:rotate-12 transition-transform duration-300">
                        {secondaryAction.icon}
                      </span>
                    )}
                  </Link>
                )
              )}
            </div>
          )}

          {/* Enhanced Stats Preview */}
          {stats.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
              {stats.map((stat, index) => (
                <div key={index} className="text-center group bg-card/30 p-4 rounded-sm border border-border/30 hover:border-primary/30 hover:bg-card/50 transition-all duration-300">
                  <div className="text-2xl font-bold text-primary group-hover:scale-110 transition-transform duration-300">
                    {stat.number}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Floating Elements */}
      {floatingElements}

      {/* Scroll Indicator */}
      {scrollIndicator && (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-primary/30 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-primary/60 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      )}
    </section>
  );
}; 