/**
 * Terms of Service Page
 */

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@djangocfg/ui/components';

export default function TermsOfServicePage() {
  return (
    <div className="container mx-auto max-w-4xl py-16 px-4">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl font-bold">Terms of Service</h1>
          <p className="text-lg text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>1. Acceptance of Terms</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              By accessing and using this service, you accept and agree to be bound by the terms
              and provision of this agreement.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>2. Use License</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              Permission is granted to temporarily download one copy of the materials on our
              service for personal, non-commercial transitory viewing only.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>3. Disclaimer</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              The materials on our service are provided on an 'as is' basis. We make no warranties,
              expressed or implied, and hereby disclaim and negate all other warranties including,
              without limitation, implied warranties or conditions of merchantability, fitness for a
              particular purpose, or non-infringement of intellectual property or other violation of
              rights.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>4. Limitations</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              In no event shall we or our suppliers be liable for any damages (including, without
              limitation, damages for loss of data or profit, or due to business interruption)
              arising out of the use or inability to use the materials on our service.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>5. Revisions</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We may revise these terms of service at any time without notice. By using this
              service you are agreeing to be bound by the then current version of these terms of
              service.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
