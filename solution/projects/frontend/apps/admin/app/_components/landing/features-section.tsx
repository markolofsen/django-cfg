'use client'

import { FeatureSection } from '@djangocfg/ui-nextjs/blocks'
import {
  Database,
  Shield,
  Zap,
  Bot,
  Layout,
  Settings,
  Users,
  CreditCard,
  Bell,
  FileText
} from 'lucide-react'

const features = [
  {
    icon: <Bot className="w-6 h-6" />,
    title: "AI-Native Docs",
    description: "MCP server for Claude, Cursor, GPT. Your AI assistant can search docs instantly."
  },
  {
    icon: <Database className="w-6 h-6" />,
    title: "Multi-Database",
    description: "PostgreSQL, MySQL, SQLite with automatic routing and connection pooling."
  },
  {
    icon: <Layout className="w-6 h-6" />,
    title: "Next.js Admin",
    description: "Modern React admin with Tailwind CSS. Auto-generated TypeScript types."
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: "JWT Authentication",
    description: "Secure token-based auth with refresh tokens and role-based access control."
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: "Background Tasks",
    description: "Django-RQ with Redis. 10K+ jobs/sec with built-in monitoring dashboard."
  },
  {
    icon: <Settings className="w-6 h-6" />,
    title: "Type-Safe Config",
    description: "Pydantic v2 settings with validation, environment variables, and secrets."
  },
  {
    icon: <Users className="w-6 h-6" />,
    title: "User Management",
    description: "Complete accounts app with profiles, roles, and permissions."
  },
  {
    icon: <CreditCard className="w-6 h-6" />,
    title: "Payments Ready",
    description: "Multi-provider payments with NowPayments, CryptAPI, automatic failover."
  },
  {
    icon: <Bell className="w-6 h-6" />,
    title: "Notifications",
    description: "Email, Telegram, and push notifications with templates."
  },
  {
    icon: <FileText className="w-6 h-6" />,
    title: "API Documentation",
    description: "Auto-generated OpenAPI docs with Swagger UI and ReDoc."
  }
]

export function FeaturesSection() {
  return (
    <FeatureSection
      title="Everything You Need"
      subtitle="Production-ready features out of the box. Focus on your business logic, not infrastructure."
      features={features}
    />
  )
}
