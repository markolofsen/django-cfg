import {
    Badge, ButtonLink, Card, CardContent, CardDescription, CardHeader, CardTitle
} from '@djangocfg/ui-nextjs';
import { routes } from '@routes/admin';

/**
 * Admin Demo Page
 *
 * This is a demo admin panel showcasing Django-CFG's Next.js integration.
 * It demonstrates how external Next.js apps can be embedded in Django Admin.
 */
export default function AdminIndexPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4">Demo Admin Panel</Badge>
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Django-CFG Admin Integration
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            This Next.js app is embedded in Django Admin via iframe.
            JWT tokens are automatically injected for authentication.
          </p>
        </div>

        {/* How it works */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
            <CardDescription>
              Django-CFG dual-tab admin architecture
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 rounded-lg border bg-muted/50">
                <h3 className="font-semibold mb-2">Tab 1: Built-in Dashboard</h3>
                <p className="text-sm text-muted-foreground">
                  Served from <code className="text-xs bg-muted px-1 py-0.5 rounded">/cfg/admin/</code> -
                  Django-CFG's internal Next.js app with system monitoring tools.
                </p>
              </div>
              <div className="p-4 rounded-lg border bg-primary/5 border-primary/20">
                <h3 className="font-semibold mb-2">Tab 2: External Admin (This)</h3>
                <p className="text-sm text-muted-foreground">
                  Served from <code className="text-xs bg-muted px-1 py-0.5 rounded">/cfg/nextjs-admin/</code> -
                  Your custom Next.js admin panel.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-lg border">
              <h4 className="font-medium mb-2">Development vs Production</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <strong>Dev mode:</strong> iframe loads <code className="text-xs bg-muted px-1 py-0.5 rounded">localhost:3000</code> (hot reload works!)</li>
                <li>• <strong>Production:</strong> Static HTML served from ZIP archive</li>
                <li>• JWT tokens injected automatically via postMessage / HTML injection</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Navigation */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Demo Pages</CardTitle>
            <CardDescription>
              Example pages in this admin panel
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-3">
              <ButtonLink href={routes.crypto.path} variant="outline" className="h-auto py-4 flex-col">
                <span className="font-medium">{routes.crypto.metadata.label}</span>
                <span className="text-xs text-muted-foreground">{routes.crypto.metadata.description}</span>
              </ButtonLink>
              <ButtonLink href={routes.trading.path} variant="outline" className="h-auto py-4 flex-col">
                <span className="font-medium">{routes.trading.metadata.label}</span>
                <span className="text-xs text-muted-foreground">{routes.trading.metadata.description}</span>
              </ButtonLink>
              <ButtonLink href="/admin/landing" variant="outline" className="h-auto py-4 flex-col">
                <span className="font-medium">Landing</span>
                <span className="text-xs text-muted-foreground">Demo landing page</span>
              </ButtonLink>
            </div>
          </CardContent>
        </Card>

        {/* Documentation link */}
        <Card>
          <CardHeader>
            <CardTitle>Documentation</CardTitle>
            <CardDescription>
              Learn how to create your own custom admin panel
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col sm:flex-row gap-3">
            <ButtonLink
              href="https://djangocfg.com/docs/guides/nextjs-admin-setup"
              target="_blank"
              className="flex-1"
            >
              Setup Guide
            </ButtonLink>
            <ButtonLink
              href="https://djangocfg.com/docs/features/integrations/nextjs-admin"
              variant="outline"
              target="_blank"
              className="flex-1"
            >
              Integration Docs
            </ButtonLink>
            <ButtonLink
              href="https://djangocfg.com/docs/guides/nextjs-admin-setup/troubleshooting"
              variant="outline"
              target="_blank"
              className="flex-1"
            >
              Troubleshooting
            </ButtonLink>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-muted-foreground">
          <p>
            Django-CFG External Admin Demo •
            <a
              href="https://djangocfg.com"
              target="_blank"
              className="underline hover:text-foreground ml-1"
            >
              djangocfg.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
