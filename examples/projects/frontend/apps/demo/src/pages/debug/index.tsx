/**
 * Debug Tools - Landing Page
 *
 * Central hub for all debugging and testing tools
 * Only available in development mode
 */

'use client';

import Link from 'next/link';
import { Bug, FileQuestion, ServerCrash, Wrench, ArrowRight } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Alert,
  AlertDescription,
  Badge,
} from '@djangocfg/ui/components';

export default function DebugIndexPage() {
  return (
    <div className="container mx-auto max-w-6xl py-16 px-4">
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-4">
          <h1 className="text-4xl font-bold">Debug Tools</h1>
          <p className="text-lg text-muted-foreground">
            Testing and debugging utilities for development
          </p>
        </div>

        {/* Warning Banner */}
        <Alert>
          <AlertDescription>
            ⚠️ These tools are for development and testing purposes only
          </AlertDescription>
        </Alert>

        {/* Debug Tools Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Runtime Error Test */}
          <Link href="/debug/error" className="group">
            <Card className="h-full transition-colors hover:border-primary">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-destructive/10 rounded-lg">
                      <Bug className="w-6 h-6 text-destructive" />
                    </div>
                    <CardTitle className="group-hover:text-primary">Runtime Error</CardTitle>
                  </div>
                  <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Test ErrorBoundary by throwing an intentional runtime error
                </CardDescription>
              </CardContent>
            </Card>
          </Link>

          {/* 404 Error Page */}
          <Link href="/404" className="group">
            <Card className="h-full transition-colors hover:border-primary">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-muted/50 rounded-lg">
                      <FileQuestion className="w-6 h-6 text-muted-foreground" />
                    </div>
                    <CardTitle className="group-hover:text-primary">404 Page</CardTitle>
                  </div>
                  <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Preview the 404 Not Found error page
                </CardDescription>
              </CardContent>
            </Card>
          </Link>

          {/* 500 Error Page */}
          <Link href="/500" className="group">
            <Card className="h-full transition-colors hover:border-primary">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-destructive/10 rounded-lg">
                      <ServerCrash className="w-6 h-6 text-destructive" />
                    </div>
                    <CardTitle className="group-hover:text-primary">500 Page</CardTitle>
                  </div>
                  <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Preview the 500 Server Error page
                </CardDescription>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Additional Info */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <Wrench className="w-5 h-5 text-muted-foreground" />
              <CardTitle>About Debug Tools</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>
              These debug tools help you test error handling, layouts, and other critical
              functionality during development.
            </p>
            <p>
              All error pages use the <strong className="text-foreground">ErrorLayout</strong> component with automatic
              configuration based on error codes. The <strong className="text-foreground">ErrorBoundary</strong> component
              automatically catches React runtime errors.
            </p>
          </CardContent>
        </Card>

        {/* Configuration Details */}
        <Card>
          <CardHeader>
            <CardTitle>Error Handling Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <span className="text-muted-foreground">•</span>
              <div>
                <strong>ErrorBoundary:</strong>{' '}
                <span className="text-muted-foreground">
                  Configured in appLayoutConfig.errors (enabled by default)
                </span>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-muted-foreground">•</span>
              <div>
                <strong>Support Email:</strong>{' '}
                <span className="text-muted-foreground">
                  Pulled from settings.contact.email
                </span>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-muted-foreground">•</span>
              <div>
                <strong>Auto-Configuration:</strong>{' '}
                <span className="text-muted-foreground">
                  Error content (title, description, icon) auto-generated from error codes
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
