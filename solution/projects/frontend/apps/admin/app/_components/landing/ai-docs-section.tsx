'use client'

import { Card, CardContent, Badge, CopyButton } from '@djangocfg/ui-nextjs'
import { PrettyCode } from '@djangocfg/ui-nextjs'
import { Bot, Terminal, Plug } from 'lucide-react'

const mcpConfig = `{
  "mcpServers": {
    "djangocfg-docs": {
      "url": "https://mcp.djangocfg.com/mcp"
    }
  }
}`

const features = [
  {
    icon: <Plug className="w-5 h-5" />,
    title: "MCP Server",
    description: "Add to Claude Desktop or Cursor config for instant docs access"
  },
  {
    icon: <Terminal className="w-5 h-5" />,
    title: "CLI Tools",
    description: "Search docs from terminal: manage.py ai_docs search \"query\""
  },
  {
    icon: <Bot className="w-5 h-5" />,
    title: "CLAUDE.md",
    description: "Auto-detected hints in every project directory"
  }
]

export function AIDocsSection() {
  return (
    <section className="py-16 sm:py-20 md:py-24 bg-muted/30">
      <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4">
            <Bot className="w-3 h-3 mr-1" />
            AI-Native Documentation
          </Badge>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            Your AI Knows Django-CFG
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            First Django framework with MCP server. Claude, Cursor, GPT can access documentation instantly.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 items-start">
          {/* MCP Config */}
          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <div className="p-4 border-b flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plug className="w-4 h-4 text-primary" />
                  <span className="font-medium">claude_desktop_config.json</span>
                </div>
                <Badge variant="secondary">MCP Server</Badge>
              </div>
              <div className="p-4">
                <PrettyCode data={mcpConfig} language="json" />
              </div>
              <div className="p-4 border-t bg-muted/30">
                <p className="text-sm text-muted-foreground">
                  Add this to your AI assistant config and get instant access to all DjangoCFG documentation.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <div className="space-y-4">
            {features.map((feature, index) => (
              <Card key={index} className="transition-all hover:shadow-md">
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary shrink-0">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold mb-1">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* CLI Example */}
            <Card className="bg-zinc-950 text-zinc-100 overflow-hidden">
              <CardContent className="p-4 font-mono text-sm">
                <div className="flex items-center gap-2 text-zinc-500 mb-2">
                  <Terminal className="w-4 h-4" />
                  <span>Terminal</span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-green-400">$</span>
                    <code>poetry run python manage.py ai_docs search "database"</code>
                  </div>
                  <div className="text-zinc-400 pl-4">
                    1. Database Configuration<br />
                    &nbsp;&nbsp;&nbsp;How to configure PostgreSQL...<br />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  )
}
