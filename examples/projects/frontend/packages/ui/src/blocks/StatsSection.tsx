import React from 'react';

import { Card, CardContent } from '../components/card';
import { cn } from '../lib/utils';

interface Stat {
  number: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
}

interface StatsSectionProps {
  title: string;
  subtitle?: string;
  stats: Stat[];
  columns?: 2 | 3 | 4;
  className?: string;
  background?: 'dark' | 'card' | 'gradient';
}

export const StatsSection: React.FC<StatsSectionProps> = ({
  title,
  subtitle,
  stats,
  columns = 4,
  className,
  background = 'dark'
}) => {
  const getGridClasses = () => {
    switch (columns) {
      case 2:
        return 'grid-cols-1 sm:grid-cols-2';
      case 3:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
      case 4:
        return 'grid-cols-2 sm:grid-cols-2 lg:grid-cols-4';
      default:
        return 'grid-cols-2 sm:grid-cols-2 lg:grid-cols-4';
    }
  };

  const getBackgroundClasses = () => {
    switch (background) {
      case 'dark':
        return 'bg-background';
      case 'card':
        return 'gradient-card';
      case 'gradient':
        return 'gradient-subtle';
      default:
        return 'bg-background';
    }
  };

  return (
    <section className={cn('py-12 sm:py-16 lg:py-24', getBackgroundClasses(), className)}>
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12 sm:mb-16 animate-fade-in">
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
          {stats.map((stat, index) => (
            <Card 
              key={index} 
              className="text-center hover:shadow-large transition-all duration-300 animate-scale-in backdrop-blur-sm border-border/50 hover:border-primary/30 group"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardContent className="p-6 sm:p-8">
                {stat.icon && (
                  <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 group-hover:scale-110 transition-transform duration-300 shadow-brand">
                    <div className="text-white text-xl sm:text-2xl">
                      {stat.icon}
                    </div>
                  </div>
                )}
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-2 sm:mb-3 group-hover:text-primary transition-colors duration-300">
                  {stat.number}
                </div>
                <div className="text-sm sm:text-base text-muted-foreground font-medium">
                  {stat.label}
                </div>
                {stat.description && (
                  <p className="text-xs sm:text-sm text-muted-foreground mt-2">
                    {stat.description}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}; 