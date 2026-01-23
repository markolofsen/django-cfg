import type { Metadata } from 'next';
import { generateMetadata } from '@core/metadata';
import { ProfileLayout } from '@djangocfg/layouts';

export const metadata: Metadata = generateMetadata({
  title: 'Profile',
  description: 'Manage your account settings and profile information',
});

export default function ProfilePage() {
  return <ProfileLayout />;
}
