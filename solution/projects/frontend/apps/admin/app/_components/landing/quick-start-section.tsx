'use client'

import { Card, CardContent, CardHeader, CardTitle, Badge, CopyButton } from '@djangocfg/ui-nextjs'
import { Terminal, FileCode, Database, Rocket } from 'lucide-react'

const steps = [
  {
    icon: <Terminal className="w-5 h-5" />,
    title: "1. Configure Environment",
    description: "Edit your .env file with database and secret settings",
    code: "nano api/environment/.env",
    badge: "Required"
  },
  {
    icon: <Database className="w-5 h-5" />,
    title: "2. Run Migrations",
    description: "Create database tables and initial data",
    code: "poetry run python manage.py migrate",
    badge: null
  },
  {
    icon: <FileCode className="w-5 h-5" />,
    title: "3. Create Superuser",
    description: "Set up your admin account",
    code: "poetry run python manage.py superuser",
    badge: null
  },
  {
    icon: <Rocket className="w-5 h-5" />,
    title: "4. Start Server",
    description: "Launch the development server",
    code: "poetry run python manage.py runserver",
    badge: null
  }
]

export function QuickStartSection() {
  return (
    <section className="py-16 sm:py-20 md:py-24">
      <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4">
            <Terminal className="w-3 h-3 mr-1" />
            Quick Start
          </Badge>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            Get Started in Minutes
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Your project is almost ready. Just a few commands to go.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {steps.map((step, index) => (
            <Card key={index} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    {step.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-lg">{step.title}</CardTitle>
                      {step.badge && (
                        <Badge variant="secondary" className="text-xs">
                          {step.badge}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {step.description}
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 p-3 bg-zinc-950 text-zinc-100 rounded-lg font-mono text-sm">
                  <span className="text-green-400">$</span>
                  <code className="flex-1">{step.code}</code>
                  <CopyButton
                    value={step.code}
                    variant="ghost"
                    className="h-6 w-6 text-zinc-400 hover:text-zinc-100"
                    iconClassName="w-3 h-3"
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Card className="inline-block">
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground mb-2">
                After setup, access your application at:
              </p>
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <a href="http://localhost:8000/admin/" className="text-primary hover:underline">
                  Admin Panel
                </a>
                <span className="text-muted-foreground">|</span>
                <a href="http://localhost:8000/api/docs/" className="text-primary hover:underline">
                  API Docs
                </a>
                <span className="text-muted-foreground">|</span>
                <a href="http://localhost:8000/cfg/health/" className="text-primary hover:underline">
                  Health Check
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
