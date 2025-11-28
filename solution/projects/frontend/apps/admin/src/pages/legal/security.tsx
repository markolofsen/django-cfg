/**
 * Security Policy Page
 */

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@djangocfg/ui/components';

export default function SecurityPolicyPage() {
  return (
    <div className="container mx-auto max-w-4xl py-16 px-4">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-4">
          <h1 className="text-4xl font-bold">Security Policy</h1>
          <p className="text-lg text-muted-foreground">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Our Commitment to Security</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We take the security of your data seriously. We implement industry-standard
              security measures to protect your personal information from unauthorized access,
              disclosure, alteration, and destruction.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Encryption</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              All data transmitted between your device and our servers is encrypted using
              industry-standard SSL/TLS protocols. Sensitive data stored in our databases is
              encrypted at rest using advanced encryption standards.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Access Controls</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              Access to user data is strictly limited to authorized personnel who require it
              to perform their job functions. We employ multi-factor authentication and
              regular access reviews to ensure that only authorized individuals can access
              sensitive information.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Security Monitoring</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We continuously monitor our systems for potential security threats and
              vulnerabilities. Our security team actively tracks and responds to any
              suspicious activity or potential security incidents.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Reporting Security Issues</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              If you discover a security vulnerability or have concerns about our security
              practices, please report it to us immediately. We appreciate responsible
              disclosure and will work with you to address any legitimate security concerns.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Regular Security Updates</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            <p>
              We regularly update our systems and software to ensure that known security
              vulnerabilities are patched promptly. Our infrastructure undergoes periodic
              security audits and penetration testing to identify and address potential
              weaknesses.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
