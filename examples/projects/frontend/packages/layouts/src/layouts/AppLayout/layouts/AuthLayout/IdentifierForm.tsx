import React, { useState, useEffect } from 'react';
import { Mail, Phone, User, Send } from 'lucide-react';

import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Checkbox,
  Input,
  Label,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  PhoneInput,
} from '@djangocfg/ui/components';

import { useAuthContext } from './AuthContext';
import { AuthHelp } from './AuthHelp';

export const IdentifierForm: React.FC = () => {
  const {
    identifier,
    channel,
    isLoading,
    acceptedTerms,
    termsUrl,
    privacyUrl,
    enablePhoneAuth,
    setIdentifier,
    setChannel,
    setAcceptedTerms,
    handleIdentifierSubmit,
    detectChannelFromIdentifier,
    validateIdentifier,
    error,
  } = useAuthContext();

  const [localChannel, setLocalChannel] = useState<'email' | 'phone'>(channel);

  // Sync localChannel with channel from context (for localStorage updates)
  useEffect(() => {
    setLocalChannel(channel);
  }, [channel]);

  // Force email channel if phone auth is disabled
  useEffect(() => {
    if (!enablePhoneAuth && localChannel === 'phone') {
      setLocalChannel('email');
      setChannel('email');
      // Clear identifier if it's a phone number
      if (identifier && detectChannelFromIdentifier(identifier) === 'phone') {
        setIdentifier('');
      }
    }
  }, [
    enablePhoneAuth,
    localChannel,
    identifier,
    setChannel,
    setIdentifier,
    detectChannelFromIdentifier,
  ]);

  // Handle identifier change with auto-detection
  const handleIdentifierChange = (value: string) => {
    setIdentifier(value);

    // Auto-detect channel if user is typing (only if phone auth is enabled)
    const detectedChannel = detectChannelFromIdentifier(value);
    if (detectedChannel && detectedChannel !== localChannel) {
      // Only switch to phone if phone auth is enabled
      if (detectedChannel === 'phone' && !enablePhoneAuth) {
        return; // Don't switch to phone channel if disabled
      }
      setLocalChannel(detectedChannel);
      setChannel(detectedChannel);
    }
  };

  // Handle manual channel switch
  const handleChannelChange = (newChannel: 'email' | 'phone') => {
    // Prevent switching to phone if phone auth is disabled
    if (newChannel === 'phone' && !enablePhoneAuth) {
      return;
    }

    setLocalChannel(newChannel);
    setChannel(newChannel);
    // Clear identifier when switching channels
    if (identifier && !validateIdentifier(identifier, newChannel)) {
      setIdentifier('');
    }
  };

  const getChannelDescription = () => {
    return localChannel === 'phone'
      ? 'Enter your phone number to receive a verification code via SMS'
      : 'Enter your email address to receive a verification code';
  };
  
  return (
    <Card className="w-full max-w-md mx-auto shadow-lg border border-border bg-card/50 backdrop-blur-sm">
      <CardHeader className="text-center pb-6">
        <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
          <User className="w-6 h-6 text-primary" />
        </div>
        <CardTitle className="text-xl font-semibold">Sign In</CardTitle>
        <CardDescription className="text-muted-foreground">
          {getChannelDescription()}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {enablePhoneAuth ? (
          <Tabs
            value={localChannel}
            onValueChange={(value) => handleChannelChange(value as 'email' | 'phone')}
          >
            {/* Channel Selection Tabs */}
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email" className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email
              </TabsTrigger>
              <TabsTrigger value="phone" className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                Phone
              </TabsTrigger>
            </TabsList>

            <form onSubmit={handleIdentifierSubmit} className="space-y-6 mt-6">
              <TabsContent value="email" className="space-y-3 mt-0">
                <Label
                  htmlFor="identifier"
                  className="text-sm font-medium text-foreground flex items-center gap-2"
                >
                  <Mail className="w-4 h-4" />
                  Email Address
                </Label>
                <Input
                  id="identifier"
                  type="email"
                  placeholder="Enter your email address"
                  value={identifier}
                  onChange={(e) => handleIdentifierChange(e.target.value)}
                  disabled={isLoading}
                  required
                  className="h-11 text-base"
                />
              </TabsContent>

              <TabsContent value="phone" className="space-y-3 mt-0">
                <Label
                  htmlFor="phone-identifier"
                  className="text-sm font-medium text-foreground flex items-center gap-2"
                >
                  <Phone className="w-4 h-4" />
                  Phone Number
                </Label>
                <PhoneInput
                  value={identifier}
                  onChange={(value) => handleIdentifierChange(value || '')}
                  disabled={isLoading}
                  placeholder="Enter your phone number"
                  defaultCountry="US"
                  className="h-11 text-base"
                />
              </TabsContent>

              {/* Terms and Conditions */}
              <div className="flex items-start gap-3">
                <Checkbox
                  id="terms"
                  checked={acceptedTerms}
                  onCheckedChange={setAcceptedTerms}
                  disabled={isLoading}
                  className="mt-1"
                />
                <div className="text-sm text-muted-foreground leading-5">
                  <Label htmlFor="terms" className="cursor-pointer">
                    I agree to the{' '}
                    <a
                      href={termsUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline font-medium"
                    >
                      Terms of Service
                    </a>{' '}
                    and{' '}
                    <a
                      href={privacyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline font-medium"
                    >
                      Privacy Policy
                    </a>
                  </Label>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md border border-destructive/20">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full h-11 text-base font-medium"
                disabled={isLoading || !identifier || !acceptedTerms}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Sending code...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Send className="w-4 h-4" />
                    Send verification code
                  </div>
                )}
              </Button>
            </form>
          </Tabs>
        ) : (
          <form onSubmit={handleIdentifierSubmit} className="space-y-6 mt-6">
            {/* Email-only input when phone auth is disabled */}
            <div className="space-y-3">
              <Label
                htmlFor="email-only"
                className="text-sm font-medium text-foreground flex items-center gap-2"
              >
                <Mail className="w-4 h-4" />
                Email Address
              </Label>
              <Input
                id="email-only"
                type="email"
                placeholder="Enter your email address"
                value={identifier}
                onChange={(e) => handleIdentifierChange(e.target.value)}
                disabled={isLoading}
                required
                className="h-11 text-base"
              />
            </div>

            {/* Terms and Conditions */}
            <div className="flex items-start gap-3">
              <Checkbox
                id="terms-email"
                checked={acceptedTerms}
                onCheckedChange={setAcceptedTerms}
                disabled={isLoading}
                className="mt-1"
              />
              <div className="text-sm text-muted-foreground leading-5">
                <Label htmlFor="terms-email" className="cursor-pointer">
                  I agree to the{' '}
                  <a
                    href={termsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-medium"
                  >
                    Terms of Service
                  </a>{' '}
                  and{' '}
                  <a
                    href={privacyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-medium"
                  >
                    Privacy Policy
                  </a>
                </Label>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md border border-destructive/20">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full h-11 text-base font-medium"
              disabled={isLoading || !identifier || !acceptedTerms}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Sending code...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Send className="w-4 h-4" />
                  Send verification code
                </div>
              )}
            </Button>
          </form>
        )}

        {/* Help Section */}
        <AuthHelp />
      </CardContent>
    </Card>
  );
};
