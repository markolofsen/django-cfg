import { Code2, TrendingUp, Users, Zap } from 'lucide-react';

import { Card, CardContent } from '@djangocfg/ui-nextjs';

const stats = [
  {
    icon: Code2,
    value: '100%',
    label: 'Type Safe',
    description: 'Full TypeScript coverage'
  },
  {
    icon: Zap,
    value: '< 100ms',
    label: 'Fast API',
    description: 'Average response time'
  },
  {
    icon: TrendingUp,
    value: '99.9%',
    label: 'Uptime',
    description: 'Reliable & stable'
  },
  {
    icon: Users,
    value: '1000+',
    label: 'Components',
    description: 'Ready to use'
  }
];

export function StatsSection() {
  return (
    <section className="py-20 lg:py-32 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Built for performance & scale
            </h2>
            <p className="text-lg text-muted-foreground">
              Optimized for speed, reliability, and developer experience
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
              <Card key={stat.label} className="text-center hover:shadow-lg transition-all duration-300">
                <CardContent className="pt-6">
                  <div className="inline-flex items-center justify-center p-3 rounded-lg bg-primary/10 text-primary mb-4">
                    <stat.icon className="h-6 w-6" />
                  </div>
                  <div className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-lg font-semibold mb-1">{stat.label}</div>
                  <div className="text-sm text-muted-foreground">{stat.description}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
