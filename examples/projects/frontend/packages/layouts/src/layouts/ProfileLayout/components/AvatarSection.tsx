'use client';

import { Check, Upload, X } from 'lucide-react';
import React, { useState } from 'react';
import { toast } from 'sonner';

import { Avatar, AvatarFallback, Button } from '@djangocfg/ui/components';
import { useAccountsContext } from '@djangocfg/api/cfg/contexts';
import { useAuth } from '../../../auth';

export const AvatarSection = () => {
  const { user } = useAuth();
  const accounts = useAccountsContext();
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const getInitials = (name: string) => {
    if (!name) return 'UN';
    return name
      .split(' ')
      .map((word) => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File size must be less than 5MB');
        return;
      }
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setAvatarPreview(e.target?.result as string);
      reader.readAsDataURL(file);
    } else {
      setAvatarFile(null);
      setAvatarPreview(null);
    }
  };

  const handleAvatarUpload = async () => {
    if (!avatarFile) return;
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('avatar', avatarFile);
      await accounts.uploadAvatar(formData as any);
      toast.success('Avatar updated successfully');
      setAvatarFile(null);
      setAvatarPreview(null);
    } catch (error) {
      toast.error('Failed to upload avatar');
      console.error('Avatar upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const resetAvatar = () => {
    setAvatarFile(null);
    setAvatarPreview(null);
  };

  return (
    <div className="flex flex-col items-center mb-4">
      <div className="relative group">
        <Avatar className="w-24 h-24 transition-transform group-hover:scale-105">
          {avatarPreview ? (
            <img
              src={avatarPreview}
              alt="Avatar preview"
              className="w-full h-full object-cover rounded-full"
            />
          ) : user?.avatar ? (
            <img
              src={user.avatar}
              alt="User avatar"
              className="w-full h-full object-cover rounded-full"
            />
          ) : (
            <AvatarFallback className="text-2xl font-semibold bg-gradient-to-br from-primary to-primary/80 text-primary-foreground">
              {getInitials(user?.display_username || user?.email || '')}
            </AvatarFallback>
          )}
        </Avatar>

        {/* Upload overlay - appears on hover */}
        <label className="absolute inset-0 rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
          <div className="p-3 rounded-full bg-primary/80 text-primary-foreground hover:bg-primary transition-colors">
            <Upload className="w-5 h-5" />
          </div>
          <input
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
            className="hidden"
          />
        </label>

        {/* Action buttons - appear when file is selected */}
        {avatarFile && (
          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 flex items-center space-x-1 bg-card border border-border rounded-full shadow-lg p-1">
            <Button
              size="sm"
              onClick={handleAvatarUpload}
              disabled={isUploading}
              className="h-7 px-3 rounded-full"
            >
              {isUploading ? (
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white" />
              ) : (
                <Check className="w-3 h-3" />
              )}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={resetAvatar}
              className="h-7 w-7 rounded-full p-0"
            >
              <X className="w-3 h-3" />
            </Button>
          </div>
        )}
      </div>

      {/* File info - shows when file is selected */}
      {avatarFile && (
        <div className="mt-3 text-center">
          <p className="text-xs text-muted-foreground">
            {avatarFile.name} ({(avatarFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        </div>
      )}
    </div>
  );
};

