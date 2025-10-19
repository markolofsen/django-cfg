import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import {
  Zap,
  Code2,
  Palette,
  Shield,
  Boxes,
  RefreshCw
} from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Built with performance in mind. SWR for data fetching, optimistic updates, and automatic caching.'
  },
  {
    icon: Code2,
    title: 'Type-Safe',
    description: 'Full TypeScript support with auto-generated API clients from Django OpenAPI schema.'
  },
  {
    icon: Palette,
    title: 'Beautiful UI',
    description: 'Modern design system with shadcn/ui components, dark mode, and responsive layouts.'
  },
  {
    icon: Shield,
    title: 'Production Ready',
    description: 'Built-in authentication, error handling, and best practices for scalable applications.'
  },
  {
    icon: Boxes,
    title: 'Modular Architecture',
    description: 'Clean separation of concerns with reusable contexts, hooks, and component patterns.'
  },
  {
    icon: RefreshCw,
    title: 'Real-time Updates',
    description: 'Automatic revalidation and real-time data synchronization across your application.'
  }
];

export function FeaturesSection() {
  return (
    <section className="py-20 lg:py-32">
      <div className="container mx-auto px-6">
        <div className="max-w-3xl mx-auto text-center mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight">
            Everything you need to build
          </h2>
          <p className="text-lg text-muted-foreground">
            A complete full-stack solution with all the tools and patterns you need to ship faster.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/50">
              <CardHeader>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
