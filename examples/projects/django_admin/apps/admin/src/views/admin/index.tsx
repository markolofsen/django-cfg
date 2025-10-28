import React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  useCopy,
} from '@djangocfg/ui';
import {
  Lock,
  ExternalLink,
  Copy,
} from 'lucide-react';
import { settings } from '@/core/settings';

export default function AdminView() {
  const { copyToClipboard } = useCopy();

  const adminUrl = settings.admin.url;
  const demoEmail = settings.admin.demo.email;
  const demoPassword = settings.admin.demo.password;

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4">
      <div className="space-y-6">
        {/* Hero Block */}
        <div className="text-center space-y-4 py-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
            <Lock className="h-4 w-4" />
            Admin Panel Demo
          </div>
          <h1 className="text-4xl font-bold tracking-tight">
            Django Admin Interface
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Experience the powerful Django CFG administration panel with full access to manage models, users, and system configuration
          </p>
        </div>

        {/* Main Card */}
        <Card>
          <CardHeader>
            <CardTitle>Demo Access</CardTitle>
            <CardDescription>
              Use these credentials to login to the Django admin panel
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Credentials */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <div className="flex gap-2">
                  <code className="flex-1 rounded bg-muted px-3 py-2 text-sm font-mono">
                    {demoEmail}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(demoEmail, "Email copied!")}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <div className="flex gap-2">
                  <code className="flex-1 rounded bg-muted px-3 py-2 text-sm font-mono">
                    {demoPassword}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(demoPassword, "Password copied!")}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Open Button */}
            <div className="flex justify-center pt-4">
              <Button
                size="lg"
                className="gap-2"
                onClick={() => window.open(adminUrl, '_blank')}
              >
                <Lock className="h-4 w-4" />
                Open Admin Panel
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card>
          <CardHeader>
            <CardTitle>About Django Admin</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Django admin is a powerful, production-ready interface automatically generated from your models.
              It provides a clean way to manage your application's data, users, permissions, and system configuration.
              Django CFG extends this with real-time updates and advanced features.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
