import { Mail, MessageCircle, HelpCircle } from 'lucide-react';
import React from 'react';

import { Button } from '@djangocfg/ui/components';

import { useAuthContext } from './AuthContext';

import type { AuthHelpProps } from './types';

export const AuthHelp: React.FC<AuthHelpProps> = ({
  className = '',
  variant = 'default',
}) => {
  const { supportUrl, channel } = useAuthContext();

  const getChannelIcon = () => {
    return channel === 'phone' ? (
      <MessageCircle className="w-4 h-4 text-muted-foreground" />
    ) : (
      <Mail className="w-4 h-4 text-muted-foreground" />
    );
  };

  const getHelpText = () => {
    return channel === 'phone' ? 'Check WhatsApp/SMS' : 'Check spam folder';
  };

  const getDetailedHelp = () => {
    if (channel === 'phone') {
      return {
        title: "Didn't receive the code?",
        tips: [
          '• Check your WhatsApp messages',
          '• Look for SMS messages',
          '• Ensure you have signal/internet',
          '• Wait a few minutes for delivery',
        ],
      };
    } else {
      return {
        title: "Didn't receive the email?",
        tips: [
          '• Check your spam or junk folder',
          '• Make sure you entered the correct email address',
          '• Wait a few minutes for the email to arrive',
        ],
      };
    }
  };

  if (variant === 'compact') {
    return (
      <div
        className={`flex items-center justify-between p-3 bg-muted/30 rounded-sm border border-border ${className}`}
      >
        <div className="flex items-center gap-2">
          {getChannelIcon()}
          <span className="text-sm text-muted-foreground">{getHelpText()}</span>
        </div>
        {supportUrl && (
          <Button
            asChild
            variant="ghost"
            size="sm"
            className="text-xs"
          >
            <a href={supportUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1">
              <HelpCircle className="w-3 h-3" />
              Need help?
            </a>
          </Button>
        )}
      </div>
    );
  }

  const helpData = getDetailedHelp();

  return (
    <div
      className={`flex flex-col gap-3 p-3 bg-muted/30 rounded-sm border border-border ${className}`}
    >
      <div className="flex items-start gap-3">
        {getChannelIcon()}
        <div className="flex flex-col gap-1">
          <h4 className="text-sm font-medium text-foreground">{helpData.title}</h4>
          <div className="flex flex-col gap-0.5 text-xs text-muted-foreground">
            {helpData.tips.map((tip, index) => (
              <p key={index}>{tip}</p>
            ))}
          </div>
        </div>
      </div>

      {supportUrl && (
        <div className="flex items-center justify-between pt-2 border-t border-border">
          <span className="text-xs text-muted-foreground">Still having trouble?</span>
          <Button
            asChild
            variant="ghost"
            size="sm"
            className="text-xs h-7 px-2"
          >
            <a href={supportUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1">
              <HelpCircle className="w-3 h-3" />
              Get Help
            </a>
          </Button>
        </div>
      )}
    </div>
  );
};
