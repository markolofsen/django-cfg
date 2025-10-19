import { ReactNode } from 'react';

import { cn } from '../lib/utils';

interface SectionProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "dark" | "gradient" | "card";
  size?: "sm" | "md" | "lg" | "xl";
}

export const Section = ({ 
  children, 
  className, 
  variant = "default",
  size = "lg" 
}: SectionProps) => {
  const paddingClasses = {
    sm: "py-12",
    md: "py-16", 
    lg: "py-24",
    xl: "py-32"
  };

  const variantClasses = {
    default: "bg-background",
    dark: "bg-card relative",
    gradient: "gradient-hero relative overflow-hidden",
    card: "gradient-card relative"
  };

  return (
    <section className={cn('section-padding', variantClasses[variant], className)}>
      <div className="w-full px-4 sm:px-6 lg:px-8">
        {children}
      </div>
    </section>
  );
};

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export const SectionHeader = ({ title, subtitle, className }: SectionHeaderProps) => (
  <div className={cn("text-center mb-16 animate-fade-in", className)}>
    <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-6">
      {title}
    </h2>
    {subtitle && (
      <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
        {subtitle}
      </p>
    )}
  </div>
); 