'use client';

import React from 'react';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@djangocfg/ui/components';
import { AccountsProvider } from '@djangocfg/api/cfg/contexts';
import { useAuth } from '../../auth';

import { AvatarSection, ProfileForm } from './components';

interface ProfileLayoutProps {
  // Callbacks
  onUnauthenticated?: () => void;

  // Optional customization
  title?: string;
  description?: string;
  showMemberSince?: boolean;
}

const ProfileContent = ({
  onUnauthenticated,
  title = 'Profile Settings',
  description = 'Manage your account information and preferences',
  showMemberSince = true
}: ProfileLayoutProps) => {
  const { user, isLoading } = useAuth();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Show auth check if no user
  if (!user && !isLoading) {
    React.useEffect(() => {
      if (onUnauthenticated) {
        onUnauthenticated();
      }
    }, [onUnauthenticated]);

    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-4">Not Authenticated</h1>
          <p className="text-muted-foreground mb-4">Please log in to view your profile.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-foreground">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>

        {/* Main Profile Card */}
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
          <CardHeader className="text-center pb-6">
            <AvatarSection />

            <CardTitle className="text-xl">
              {user?.display_username || user?.email}
            </CardTitle>
            {showMemberSince && user?.date_joined && (
              <CardDescription className="text-muted-foreground">
                Member since {formatDate(user.date_joined)}
              </CardDescription>
            )}
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Profile Form */}
            <ProfileForm />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export const ProfileLayout: React.FC<ProfileLayoutProps> = (props) => {
  return (
    <AccountsProvider>
      <ProfileContent {...props} />
    </AccountsProvider>
  );
};

