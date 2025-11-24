/**
 * Privacy Policy Page
 */

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@djangocfg/ui/components';

export default function PrivacyPolicyPage() {
  return (
    <div className="container mx-auto max-w-4xl py-16 px-4">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl font-bold">Privacy Policy</h1>
          <p className="text-lg text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Information We Collect</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We collect information that you provide directly to us, including when you create an
              account, use our services, or communicate with us.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>How We Use Your Information</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground flex flex-col gap-2">
            <p>We use the information we collect to:</p>
            <ul className="list-disc list-inside flex flex-col gap-1 ml-4">
              <li>Provide, maintain, and improve our services</li>
              <li>Process transactions and send related information</li>
              <li>Send technical notices and support messages</li>
              <li>Respond to your comments and questions</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Information Sharing</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We do not share your personal information with third parties except as described in
              this privacy policy or with your consent.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Security</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We take reasonable measures to help protect your personal information from loss,
              theft, misuse, unauthorized access, disclosure, alteration, and destruction.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your Rights</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              You have the right to access, update, or delete your personal information at any
              time. Contact us if you wish to exercise these rights.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Changes to This Policy</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We may update this privacy policy from time to time. We will notify you of any
              changes by posting the new policy on this page.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
