/**
 * Default legal page configurations
 *
 * Pre-configured content for common legal pages
 * Can be customized or extended as needed
 */

import type { LegalPageConfig } from './types';

export const privacyConfig: LegalPageConfig = {
  title: 'Privacy Policy',
  sections: [
    {
      title: 'Information We Collect',
      content: 'We collect information that you provide directly to us, including when you create an account, use our services, or communicate with us.',
    },
    {
      title: 'How We Use Your Information',
      content: [
        'We use the information we collect to:',
        'Provide, maintain, and improve our services',
        'Process transactions and send related information',
        'Send technical notices and support messages',
        'Respond to your comments and questions',
      ],
    },
    {
      title: 'Information Sharing',
      content: 'We do not share your personal information with third parties except as described in this privacy policy or with your consent.',
    },
    {
      title: 'Data Security',
      content: 'We take reasonable measures to help protect your personal information from loss, theft, misuse, unauthorized access, disclosure, alteration, and destruction.',
    },
    {
      title: 'Your Rights',
      content: 'You have the right to access, update, or delete your personal information at any time. Contact us if you wish to exercise these rights.',
    },
    {
      title: 'Changes to This Policy',
      content: 'We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page.',
    },
  ],
};

export const termsConfig: LegalPageConfig = {
  title: 'Terms of Service',
  sections: [
    {
      title: '1. Acceptance of Terms',
      content: 'By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement.',
    },
    {
      title: '2. Use License',
      content: 'Permission is granted to temporarily download one copy of the materials on our service for personal, non-commercial transitory viewing only.',
    },
    {
      title: '3. Disclaimer',
      content: 'The materials on our service are provided on an \'as is\' basis. We make no warranties, expressed or implied, and hereby disclaim and negate all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.',
    },
    {
      title: '4. Limitations',
      content: 'In no event shall we or our suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on our service.',
    },
    {
      title: '5. Revisions',
      content: 'We may revise these terms of service at any time without notice. By using this service you are agreeing to be bound by the then current version of these terms of service.',
    },
  ],
};

export const cookiesConfig: LegalPageConfig = {
  title: 'Cookie Policy',
  sections: [
    {
      title: 'What Are Cookies?',
      content: 'Cookies are small text files that are placed on your device when you visit our website. They help us provide you with a better experience by remembering your preferences and understanding how you use our site.',
    },
    {
      title: 'Types of Cookies We Use',
      content: [
        'Essential Cookies: These cookies are necessary for the website to function properly.',
        'Performance Cookies: These cookies help us understand how visitors interact with our website.',
        'Functionality Cookies: These cookies allow us to remember choices you make and provide enhanced features.',
      ],
    },
    {
      title: 'Managing Cookies',
      content: 'Most web browsers allow you to control cookies through their settings. You can set your browser to refuse cookies or delete certain cookies. However, please note that if you disable cookies, some features of our website may not function properly.',
    },
    {
      title: 'Third-Party Cookies',
      content: 'We may use third-party services that also use cookies. These third parties have their own privacy policies, and we do not accept any responsibility or liability for their policies.',
    },
    {
      title: 'Updates to This Policy',
      content: 'We may update our Cookie Policy from time to time. Any changes will be posted on this page with an updated revision date.',
    },
  ],
};

export const securityConfig: LegalPageConfig = {
  title: 'Security Policy',
  sections: [
    {
      title: 'Our Commitment to Security',
      content: 'We take the security of your data seriously. We implement industry-standard security measures to protect your personal information from unauthorized access, disclosure, alteration, and destruction.',
    },
    {
      title: 'Data Encryption',
      content: 'All data transmitted between your device and our servers is encrypted using industry-standard SSL/TLS protocols. Sensitive data stored in our databases is encrypted at rest using advanced encryption standards.',
    },
    {
      title: 'Access Controls',
      content: 'Access to user data is strictly limited to authorized personnel who require it to perform their job functions. We employ multi-factor authentication and regular access reviews to ensure that only authorized individuals can access sensitive information.',
    },
    {
      title: 'Security Monitoring',
      content: 'We continuously monitor our systems for potential security threats and vulnerabilities. Our security team actively tracks and responds to any suspicious activity or potential security incidents.',
    },
    {
      title: 'Reporting Security Issues',
      content: 'If you discover a security vulnerability or have concerns about our security practices, please report it to us immediately. We appreciate responsible disclosure and will work with you to address any legitimate security concerns.',
    },
    {
      title: 'Regular Security Updates',
      content: 'We regularly update our systems and software to ensure that known security vulnerabilities are patched promptly. Our infrastructure undergoes periodic security audits and penetration testing to identify and address potential weaknesses.',
    },
  ],
};

