import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Input,
  Label,
  useToast,
  Separator
} from '@djangocfg/ui';
import { useProfile } from '../../contexts/ProfileContext';
import { User, Mail, Building2, Briefcase, Globe, Github, Twitter, Linkedin, Save } from 'lucide-react';

export default function ProfileView() {
  const { profile, isLoading, error, updateProfile } = useProfile();
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [formData, setFormData] = useState({
    website: profile?.website || '',
    github: profile?.github || '',
    twitter: profile?.twitter || '',
    linkedin: profile?.linkedin || '',
    company: profile?.company || '',
    job_title: profile?.job_title || ''
  });

  React.useEffect(() => {
    if (profile) {
      setFormData({
        website: profile.website || '',
        github: profile.github || '',
        twitter: profile.twitter || '',
        linkedin: profile.linkedin || '',
        company: profile.company || '',
        job_title: profile.job_title || ''
      });
    }
  }, [profile]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateProfile(formData);
      setIsEditing(false);
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to update profile. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="h-6 w-32 bg-muted animate-pulse rounded" />
            <div className="h-4 w-48 bg-muted animate-pulse rounded mt-2" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                <div className="h-10 w-full bg-muted animate-pulse rounded" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive">Failed to load profile. Please try again.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account settings and profile information
          </p>
        </div>
        {!isEditing ? (
          <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
        ) : (
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => {
              setIsEditing(false);
              setFormData({
                website: profile?.website || '',
                github: profile?.github || '',
                twitter: profile?.twitter || '',
                linkedin: profile?.linkedin || '',
                company: profile?.company || '',
                job_title: profile?.job_title || ''
              });
            }}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              <Save className="mr-2 h-4 w-4" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* User Info Card */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>User Information</CardTitle>
            <CardDescription>Basic account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="font-medium">{profile?.user_info?.username || 'User'}</p>
                <p className="text-sm text-muted-foreground">
                  {profile?.user_info?.email || 'No email'}
                </p>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">Member since</p>
                <p className="text-sm font-medium">
                  {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Last updated</p>
                <p className="text-sm font-medium">
                  {profile?.updated_at ? new Date(profile.updated_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <p className="text-sm font-medium">Activity Stats</p>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Posts</span>
                  <span className="font-medium">{profile?.posts_count || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Comments</span>
                  <span className="font-medium">{profile?.comments_count || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Orders</span>
                  <span className="font-medium">{profile?.orders_count || 0}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Profile Details Card */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Profile Details</CardTitle>
            <CardDescription>
              {isEditing ? 'Update your profile information' : 'Your public profile information'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Company & Job */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="company">
                  <Building2 className="inline h-4 w-4 mr-2" />
                  Company
                </Label>
                {isEditing ? (
                  <Input
                    id="company"
                    placeholder="Your company"
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                  />
                ) : (
                  <p className="text-sm py-2">{profile?.company || 'Not specified'}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="job_title">
                  <Briefcase className="inline h-4 w-4 mr-2" />
                  Job Title
                </Label>
                {isEditing ? (
                  <Input
                    id="job_title"
                    placeholder="Your job title"
                    value={formData.job_title}
                    onChange={(e) => handleInputChange('job_title', e.target.value)}
                  />
                ) : (
                  <p className="text-sm py-2">{profile?.job_title || 'Not specified'}</p>
                )}
              </div>
            </div>

            <Separator />

            {/* Social Links */}
            <div>
              <h3 className="text-sm font-medium mb-4">Social Links</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="website">
                    <Globe className="inline h-4 w-4 mr-2" />
                    Website
                  </Label>
                  {isEditing ? (
                    <Input
                      id="website"
                      type="url"
                      placeholder="https://your-website.com"
                      value={formData.website}
                      onChange={(e) => handleInputChange('website', e.target.value)}
                    />
                  ) : (
                    <p className="text-sm py-2">
                      {profile?.website ? (
                        <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                          {profile.website}
                        </a>
                      ) : (
                        'Not specified'
                      )}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="github">
                    <Github className="inline h-4 w-4 mr-2" />
                    GitHub
                  </Label>
                  {isEditing ? (
                    <Input
                      id="github"
                      placeholder="github.com/username"
                      value={formData.github}
                      onChange={(e) => handleInputChange('github', e.target.value)}
                    />
                  ) : (
                    <p className="text-sm py-2">
                      {profile?.github ? (
                        <a href={profile.github} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                          {profile.github}
                        </a>
                      ) : (
                        'Not specified'
                      )}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="twitter">
                    <Twitter className="inline h-4 w-4 mr-2" />
                    Twitter
                  </Label>
                  {isEditing ? (
                    <Input
                      id="twitter"
                      placeholder="twitter.com/username"
                      value={formData.twitter}
                      onChange={(e) => handleInputChange('twitter', e.target.value)}
                    />
                  ) : (
                    <p className="text-sm py-2">
                      {profile?.twitter ? (
                        <a href={profile.twitter} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                          {profile.twitter}
                        </a>
                      ) : (
                        'Not specified'
                      )}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="linkedin">
                    <Linkedin className="inline h-4 w-4 mr-2" />
                    LinkedIn
                  </Label>
                  {isEditing ? (
                    <Input
                      id="linkedin"
                      placeholder="linkedin.com/in/username"
                      value={formData.linkedin}
                      onChange={(e) => handleInputChange('linkedin', e.target.value)}
                    />
                  ) : (
                    <p className="text-sm py-2">
                      {profile?.linkedin ? (
                        <a href={profile.linkedin} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                          {profile.linkedin}
                        </a>
                      ) : (
                        'Not specified'
                      )}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
