'use client';

import { Loader2, Upload } from 'lucide-react';
import React, { useRef, useState } from 'react';
import { toast } from '@djangocfg/ui-core/hooks';

import { useAuth } from '@djangocfg/api/auth';
import { Avatar, AvatarFallback, Button } from '@djangocfg/ui-core/components';

import { useSettingsCopy } from '../i18n';
import { profileLogger } from '../../../utils/logger';

const MAX_AVATAR_BYTES = 5 * 1024 * 1024;

/**
 * Avatar header — a centered profile identity block that sits *above* the
 * settings rows, not inside one. Avatar isn't a form field like "First name";
 * it's the user's identity, so it gets the canonical Apple-ID / Slack / Linear
 * treatment: large centered avatar → name/email → a single "Change avatar"
 * action, on a soft primary-tinted hero card.
 *
 * UX: the avatar is a preview only; "Change avatar" opens the picker and
 * uploads immediately (no Save/Cancel step). The preview is optimistic — shown
 * instantly from a local object URL — and rolls back if the upload fails.
 * The whole avatar is also clickable for a faster path.
 */
export const AvatarSection = () => {
  const copy = useSettingsCopy();
  const { user, uploadAvatar } = useAuth();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handlePick = () => inputRef.current?.click();

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    // Reset so picking the same file twice still fires onChange.
    event.target.value = '';
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }
    if (file.size > MAX_AVATAR_BYTES) {
      toast.error('File size must be less than 5MB');
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setIsUploading(true);
    try {
      await uploadAvatar(file);
      toast.success('Avatar updated');
    } catch (error) {
      setPreviewUrl(null); // roll back optimistic preview
      toast.error('Failed to upload avatar');
      profileLogger.error('Avatar upload error:', error);
    } finally {
      setIsUploading(false);
      URL.revokeObjectURL(objectUrl);
      setPreviewUrl(null); // fall back to the fresh server user.avatar
    }
  };

  const displayUrl = previewUrl ?? user?.avatar ?? null;
  const displayName = user?.display_username || user?.email || '';
  // Server computes `initials` for the avatar fallback — use it verbatim
  // instead of re-deriving (keeps the letters consistent with the backend).
  const initials = user?.initials || 'UN';

  return (
    <div
      className={
        'flex flex-col items-center gap-3 rounded-2xl border border-foreground/5 px-6 pb-6 pt-8 ' +
        // Soft hero wash tinted by the theme primary — works in light and dark.
        'bg-[radial-gradient(ellipse_at_50%_0%,color-mix(in_oklab,var(--primary)_22%,transparent),transparent_70%),linear-gradient(to_bottom,color-mix(in_oklab,var(--primary)_6%,transparent),transparent)]'
      }
    >
      <button
        type="button"
        onClick={handlePick}
        disabled={isUploading}
        className="group relative rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        aria-label={copy.account.changeAvatar}
      >
        <Avatar className="h-16 w-16 overflow-hidden rounded-full ring-1 ring-foreground/10 transition-transform group-hover:scale-105 md:h-20 md:w-20">
          {displayUrl ? (
            <img src={displayUrl} alt="Avatar" className="h-full w-full object-cover" />
          ) : (
            <AvatarFallback className="bg-gradient-to-br from-primary to-primary/80 text-xl font-semibold text-primary-foreground">
              {initials}
            </AvatarFallback>
          )}
        </Avatar>

        {/* Hover / uploading overlay */}
        <span className="absolute inset-0 flex items-center justify-center rounded-full bg-black/45 text-white opacity-0 transition-opacity group-hover:opacity-100 data-[busy=true]:opacity-100"
          data-busy={isUploading}
        >
          {isUploading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Upload className="h-5 w-5" />
          )}
        </span>
      </button>

      {displayName && (
        <div className="text-center">
          <p className="text-sm font-medium text-foreground">{displayName}</p>
          {user?.email && user.display_username && (
            <p className="text-xs text-muted-foreground">{user.email}</p>
          )}
        </div>
      )}

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handlePick}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading…' : 'Change avatar'}
      </Button>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />
    </div>
  );
};
