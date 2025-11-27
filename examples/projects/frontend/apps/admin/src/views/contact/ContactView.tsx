'use client';

import { Mail, MapPin, Calendar } from 'lucide-react';
import { ContactForm, ContactInfo } from '@djangocfg/layouts';
import { Section } from '@djangocfg/ui';

const isDev = process.env.NODE_ENV === 'development';

const CONFIG = {
  apiUrl: isDev ? 'http://localhost:8000' : 'https://api.djangocfg.com',
  email: 'hello@djangocfg.com',
  calendly: 'https://calendly.com/djangocfg/meeting',
  location: 'Remote-first team',
};

export function ContactView() {
  const contactDetails = [
    {
      icon: <Mail className="h-5 w-5" />,
      label: 'Email',
      value: CONFIG.email,
      href: `mailto:${CONFIG.email}`,
    },
    {
      icon: <MapPin className="h-5 w-5" />,
      label: 'Location',
      value: CONFIG.location,
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Section className="py-16">
        <div className="container mx-auto px-4 max-w-6xl">
          {/* Header */}
          <div className="text-center mb-8 md:mb-12">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
              Get in Touch
            </h1>
            <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto px-4">
              Have a question or want to work together? We'd love to hear from you.
            </p>
          </div>

          {/* Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <ContactForm apiUrl={CONFIG.apiUrl} />
            </div>
            <div>
              <ContactInfo
                details={contactDetails}
                action={{
                  title: 'Schedule a Meeting',
                  description: 'Book a time that works for you',
                  button: {
                    icon: <Calendar className="h-4 w-4" />,
                    label: 'Book a Call',
                    href: CONFIG.calendly,
                  },
                }}
              />
            </div>
          </div>
        </div>
      </Section>
    </div>
  );
}
