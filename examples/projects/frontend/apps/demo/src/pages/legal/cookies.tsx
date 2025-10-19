/**
 * Cookie Policy Page
 */

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@djangocfg/ui/components';

export default function CookiePolicyPage() {
  return (
    <div className="container mx-auto max-w-4xl py-16 px-4">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl font-bold">Cookie Policy</h1>
          <p className="text-lg text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>What Are Cookies?</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              Cookies are small text files that are placed on your device when you visit our
              website. They help us provide you with a better experience by remembering your
              preferences and understanding how you use our site.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Types of Cookies We Use</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground flex flex-col gap-3">
            <div>
              <strong className="text-foreground">Essential Cookies:</strong>
              <p>These cookies are necessary for the website to function properly.</p>
            </div>
            <div>
              <strong className="text-foreground">Performance Cookies:</strong>
              <p>These cookies help us understand how visitors interact with our website.</p>
            </div>
            <div>
              <strong className="text-foreground">Functionality Cookies:</strong>
              <p>These cookies allow us to remember choices you make and provide enhanced features.</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Managing Cookies</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              Most web browsers allow you to control cookies through their settings. You can set
              your browser to refuse cookies or delete certain cookies. However, please note that
              if you disable cookies, some features of our website may not function properly.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Third-Party Cookies</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We may use third-party services that also use cookies. These third parties have their
              own privacy policies, and we do not accept any responsibility or liability for their
              policies.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Updates to This Policy</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We may update our Cookie Policy from time to time. Any changes will be posted on this
              page with an updated revision date.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
