import type { Metadata } from 'next';
import { ProfileLayout } from '@djangocfg/layouts';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Profile',
  description: 'Manage your account settings and profile information',
});

export default function ProfilePage() {
  return <ProfileLayout />;
}
