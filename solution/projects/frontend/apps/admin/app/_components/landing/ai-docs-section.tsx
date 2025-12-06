'use client'

import { Card, CardContent, Badge, CopyButton } from '@djangocfg/ui-nextjs'
import { Bot, Terminal, Globe } from 'lucide-react'

const options = [
  {
    icon: <Bot className="w-5 h-5" />,
    label: "MCP Server",
    desc: "Claude, Cursor, GPT",
    code: `"djangocfg-docs": { "url": "https://mcp.djangocfg.com/mcp" }`,
  },
  {
    icon: <Terminal className="w-5 h-5" />,
    label: "Python CLI",
    desc: "pip install django-cfg",
    code: `django-cfg search "database"`,
  },
  {
    icon: <Terminal className="w-5 h-5" />,
    label: "Node.js CLI",
    desc: "npm i -g @djangocfg/nextjs",
    code: `djangocfg-docs search "database"`,
  },
  {
    icon: <Globe className="w-5 h-5" />,
    label: "REST API",
    desc: "HTTP endpoint",
    code: `curl 'https://mcp.djangocfg.com/api/search?q=redis'`,
  },
]

export function AIDocsSection() {
  return (
    <section className="py-16 sm:py-20 bg-muted/30">
      <div className="container max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <Badge variant="outline" className="mb-4">
            <Bot className="w-3 h-3 mr-1" />
            AI-Native
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight mb-3">
            Your AI Knows DjangoCFG
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            First Django framework with MCP server. Access documentation via AI assistants, CLI, or API.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-4 max-w-3xl mx-auto">
          {options.map((opt, index) => (
            <Card key={index}>
              <CardContent className="p-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    {opt.icon}
                  </div>
                  <div>
                    <div className="font-semibold">{opt.label}</div>
                    <div className="text-xs text-muted-foreground">{opt.desc}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-2.5 bg-zinc-950 text-zinc-100 rounded-lg font-mono text-[11px]">
                  <code className="flex-1 overflow-x-auto">{opt.code}</code>
                  <CopyButton
                    value={opt.code}
                    variant="ghost"
                    className="h-5 w-5 text-zinc-400 hover:text-zinc-100 shrink-0"
                    iconClassName="w-3 h-3"
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
