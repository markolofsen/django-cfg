import React from 'react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/card';
import { cn } from '../lib/utils';

interface Feature {
  icon?: React.ReactNode;
  title: string;
  description: string;
  gradient?: string;
}

interface FeatureSectionProps {
  title: string;
  subtitle?: string;
  features: Feature[];
  columns?: 1 | 2 | 3 | 4;
  className?: string;
  background?: 'dark' | 'card' | 'gradient';
}

export const FeatureSection: React.FC<FeatureSectionProps> = ({
  title,
  subtitle,
  features,
  columns = 3,
  className,
  background = 'dark'
}) => {
  const getGridClasses = () => {
    switch (columns) {
      case 1:
        return 'grid-cols-1 max-w-2xl mx-auto';
      case 2:
        return 'grid-cols-1 sm:grid-cols-2';
      case 3:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
      case 4:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4';
      default:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
    }
  };

  const getBackgroundClasses = () => {
    switch (background) {
      case 'dark':
        return 'bg-muted/30';
      case 'card':
        return 'bg-card';
      case 'gradient':
        return 'bg-gradient-to-b from-background to-muted/20';
      default:
        return 'bg-background';
    }
  };

  return (
    <section className={cn('py-12 sm:py-16 lg:py-24', getBackgroundClasses(), className)}>
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12 sm:mb-16">
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4 sm:mb-6">
            {title}
          </h2>
          {subtitle && (
            <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto px-2">
              {subtitle}
            </p>
          )}
        </div>

        <div className={cn('grid gap-6 sm:gap-8', getGridClasses())}>
          {features.map((feature, index) => (
            <Card
              key={index}
              className="h-full hover:shadow-lg transition-all duration-300 backdrop-blur-sm border-border/50 hover:border-primary/30 group"
            >
              <CardHeader className="pb-4">
                {feature.icon && (
                  <div className={cn(
                    'w-12 h-12 sm:w-16 sm:h-16 rounded-lg flex items-center justify-center mb-4 sm:mb-6 group-hover:scale-110 transition-all duration-300',
                    feature.gradient || 'bg-primary/10 text-primary group-hover:bg-primary/20'
                  )}>
                    <div className="text-xl sm:text-2xl">
                      {feature.icon}
                    </div>
                  </div>
                )}
                <CardTitle className="text-lg sm:text-xl text-foreground group-hover:text-primary transition-colors duration-300">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm sm:text-base text-muted-foreground leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}; 