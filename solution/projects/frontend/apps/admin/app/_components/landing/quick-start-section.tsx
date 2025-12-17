'use client'

import { Layout, Lock, Rocket } from 'lucide-react';

import { Badge, ButtonLink, Card, CardContent } from '@djangocfg/ui-nextjs';
import { routes } from '@routes/public';

const demos = [
  {
    icon: <Layout className="w-6 h-6" />,
    title: "Admin Demo",
    description: "Explore the Django-CFG admin integration with JWT authentication and modern UI",
    href: routes.adminDemo.path,
    badge: "Public"
  },
  {
    icon: <Lock className="w-6 h-6" />,
    title: "Private Area",
    description: "See protected routes with authentication flow and user dashboard",
    href: routes.privateDemo.path,
    badge: "Auth Required"
  }
]

export function QuickStartSection() {
  return (
    <section className="py-16 sm:py-20 md:py-24">
      <div className="container max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4">
            <Rocket className="w-3 h-3 mr-1" />
            Explore
          </Badge>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            See It In Action
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Explore the demo areas to see what DjangoCFG can do for your project.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {demos.map((demo, index) => (
            <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-lg bg-primary/10 text-primary">
                    {demo.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg">{demo.title}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {demo.badge}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      {demo.description}
                    </p>
                    <ButtonLink href={demo.href} variant="outline" size="sm">
                      Open Demo
                    </ButtonLink>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
