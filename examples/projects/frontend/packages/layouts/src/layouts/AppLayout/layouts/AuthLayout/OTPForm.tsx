import React from 'react';
import { Mail, MessageCircle, ArrowLeft, RotateCw, ShieldCheck } from 'lucide-react';

import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from '@djangocfg/ui/components';

import { useAuthContext } from './AuthContext';
import { AuthHelp } from './AuthHelp';

export const OTPForm: React.FC = () => {
  const {
    identifier,
    channel,
    otp,
    isLoading,
    error,
    supportUrl,
    setOtp,
    handleOTPSubmit,
    handleResendOTP,
    handleBackToIdentifier,
  } = useAuthContext();

  const getChannelIcon = () => {
    return channel === 'phone' ? (
      <div className="flex items-center justify-center">
        <MessageCircle className="w-5 h-5 text-primary" />
      </div>
    ) : (
      <Mail className="w-5 h-5 text-primary" />
    );
  };

  const getChannelTitle = () => {
    return channel === 'phone' ? 'Verify Your Phone' : 'Verify Your Email';
  };

  const getChannelDescription = () => {
    const channelName = channel === 'phone' ? 'phone number' : 'email address';
    const method = channel === 'phone' ? 'WhatsApp/SMS' : 'email';
    return `We've sent a 6-digit verification code to your ${channelName} via ${method}`;
  };

  return (
    <Card className="w-full max-w-md mx-auto shadow-lg border border-border bg-card/50 backdrop-blur-sm">
      <CardHeader className="text-center pb-6">
        <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
          {getChannelIcon()}
        </div>
        <CardTitle className="text-xl font-semibold">{getChannelTitle()}</CardTitle>
        <CardDescription className="text-muted-foreground">
          {getChannelDescription()}
          <br />
          <span className="font-medium text-foreground">{identifier}</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <form onSubmit={handleOTPSubmit} className="space-y-6">
          <div className="space-y-3">
            <label className="text-sm font-medium text-foreground text-center block">
              Enter verification code
            </label>
            <div className="flex justify-center">
              <InputOTP
                value={otp}
                onChange={setOtp}
                maxLength={6}
                disabled={isLoading}
                containerClassName="gap-3"
              >
                <InputOTPGroup className="gap-2">
                  <InputOTPSlot
                    index={0}
                    className="h-12 w-12 text-lg font-semibold border-2 border-border bg-background rounded-sm shadow-sm"
                  />
                  <InputOTPSlot
                    index={1}
                    className="h-12 w-12 text-lg font-semibold border-2 border-border bg-background rounded-sm shadow-sm"
                  />
                  <InputOTPSlot
                    index={2}
                    className="h-12 w-12 text-lg font-semibold border-2 border-border bg-background rounded-sm shadow-sm"
                  />
                  <InputOTPSlot
                    index={3}
                    className="h-12 w-12 text-lg font-semibold border-2 border-border bg-background rounded-sm shadow-sm"
                  />
                  <InputOTPSlot
                    index={4}
                    className="h-12 w-12 text-lg font-semibold border-2 border-border bg-background rounded-sm shadow-sm"
                  />
                  <InputOTPSlot
                    index={5}
                    className="h-12 w-12 text-lg font-semibold border-2 border-border bg-background rounded-sm shadow-sm"
                  />
                </InputOTPGroup>
              </InputOTP>
            </div>
          </div>

          <div className="space-y-4">
            <Button
              type="submit"
              className="w-full h-11 text-base font-medium"
              disabled={isLoading || otp.length < 6}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Verifying...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5" />
                  Verify Code
                </div>
              )}
            </Button>

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={handleBackToIdentifier}
                disabled={isLoading}
                className="flex-1 h-10"
              >
                <div className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back
                </div>
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={handleResendOTP}
                disabled={isLoading}
                className="flex-1 h-10"
              >
                <div className="flex items-center gap-2">
                  <RotateCw className="w-4 h-4" />
                  Resend
                </div>
              </Button>
            </div>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md border border-destructive/20">
            {error}
          </div>
        )}

        {supportUrl && (
          <div className="mt-4">
            <AuthHelp />
          </div>
        )}
      </CardContent>
    </Card>
  );
};
