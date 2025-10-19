import React from 'react';

import { Card, CardContent } from '../components/card';
import { cn } from '../lib/utils';

interface Testimonial {
  content: string;
  author: {
    name: string;
    title?: string;
    company?: string;
    avatar?: string;
  };
  rating?: number;
}

interface TestimonialSectionProps {
  title?: string;
  subtitle?: string;
  testimonials: Testimonial[];
  columns?: 1 | 2 | 3;
  className?: string;
  background?: 'dark' | 'card' | 'gradient';
}

export const TestimonialSection: React.FC<TestimonialSectionProps> = ({
  title,
  subtitle,
  testimonials,
  columns = 3,
  className,
  background = 'dark'
}) => {
  // Simple Tailwind 4 classes only - no custom utilities
  const gridClasses = {
    1: 'grid-cols-1 max-w-4xl mx-auto',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  };

  const backgroundClasses = {
    dark: 'bg-background',
    card: 'bg-muted/30',
    gradient: 'bg-gradient-to-b from-background via-muted/10 to-background',
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={i < rating ? 'text-yellow-400' : 'text-neutral-400'}>
        ★
      </span>
    ));
  };

  return (
    <section className={cn(
      'relative py-16 sm:py-20 md:py-24 lg:py-32',
      backgroundClasses[background],
      className
    )}>
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {(title || subtitle) && (
          <div className="text-center mb-12 sm:mb-14 md:mb-16">
            {title && (
              <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-4 sm:mb-6">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto">
                {subtitle}
              </p>
            )}
          </div>
        )}

        <div className={cn('grid gap-6 sm:gap-8', gridClasses[columns])}>
          {testimonials.map((testimonial, index) => (
            <Card
              key={index}
              className="h-full hover:shadow-lg transition-all duration-300 backdrop-blur-sm border-border/50 hover:border-primary/30 group"
            >
              <CardContent className="p-8">
                {testimonial.rating && (
                  <div className="flex mb-6 text-lg">
                    {renderStars(testimonial.rating)}
                  </div>
                )}
                
                <blockquote className="text-foreground mb-8 italic text-lg leading-relaxed group-hover:text-primary transition-colors duration-300">
                  "{testimonial.content}"
                </blockquote>
                
                <div className="flex items-center">
                  {testimonial.author.avatar && (
                    <img
                      src={testimonial.author.avatar}
                      alt={testimonial.author.name}
                      className="w-14 h-14 rounded-full mr-4 ring-2 ring-primary/20 group-hover:ring-primary/40 transition-all duration-300"
                    />
                  )}
                  
                  <div>
                    <div className="font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
                      {testimonial.author.name}
                    </div>
                    {testimonial.author.title && (
                      <div className="text-sm text-muted-foreground">
                        {testimonial.author.title}
                        {testimonial.author.company && ` at ${testimonial.author.company}`}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}; 