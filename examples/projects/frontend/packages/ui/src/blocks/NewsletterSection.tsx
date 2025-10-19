import { Mail } from 'lucide-react';
import React from 'react';

import { Button } from '../components/button';
import { Input } from '../components/input';
import { cn } from '../lib/utils';

interface NewsletterSectionProps {
  title?: string;
  description?: string;
  placeholder?: string;
  buttonText?: string;
  disclaimer?: string;
  background?: 'default' | 'muted' | 'primary' | 'gradient';
  className?: string;
  onSubmit?: (email: string) => void;
}

/**
 * NewsletterSection - Email subscription block
 * Fully responsive and theme-aware (light/dark mode)
 * Follows Tailwind CSS v4 canons - no custom utilities
 */
export const NewsletterSection: React.FC<NewsletterSectionProps> = ({
  title = "Stay Updated with Our Newsletter",
  description = "Get the latest insights on AI, technology, and software development delivered to your inbox.",
  placeholder = "Enter your email address",
  buttonText = "Subscribe",
  disclaimer = "No spam, unsubscribe at any time",
  background = 'muted',
  className,
  onSubmit
}) => {
  const [email, setEmail] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && onSubmit) {
      onSubmit(email);
      setEmail('');
    }
  };

  // Simple Tailwind 4 classes only - no custom utilities
  // All variants work in both light and dark themes
  const backgroundClasses = {
    default: 'bg-background',
    muted: 'bg-muted/50',
    primary: 'bg-primary/5',
    gradient: 'bg-gradient-to-b from-background via-primary/5 to-background',
  };

  return (
    <section className={cn(
      'relative py-16 sm:py-20 md:py-24 lg:py-32',
      backgroundClasses[background],
      className
    )}>
      {/* Decorative background for gradient variant only */}
      {background === 'gradient' && (
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl aspect-square bg-primary/10 rounded-full blur-3xl" />
        </div>
      )}

      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto">
          {/* Title */}
          <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4 sm:mb-6">
            {title}
          </h2>

          {/* Description */}
          {description && (
            <p className="text-base sm:text-lg md:text-xl text-muted-foreground leading-relaxed mb-8 sm:mb-10 md:mb-12">
              {description}
            </p>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="max-w-md mx-auto">
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              {/* Email Input */}
              <div className="relative flex-1">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                <Input
                  type="email"
                  placeholder={placeholder}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 h-12 w-full"
                  required
                  aria-label="Email address"
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                size="lg"
                className="h-12 w-full sm:w-auto sm:min-w-[120px]"
              >
                {buttonText}
              </Button>
            </div>

            {/* Disclaimer */}
            {disclaimer && (
              <p className="text-xs sm:text-sm text-muted-foreground mt-3 text-center">
                {disclaimer}
              </p>
            )}
          </form>
        </div>
      </div>
    </section>
  );
}; 