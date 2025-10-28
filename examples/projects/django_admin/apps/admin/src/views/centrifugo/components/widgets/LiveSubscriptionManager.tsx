/**
 * Live Subscription Manager Component
 *
 * Manages active WebSocket subscriptions to Centrifugo channels
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge, Input, Popover, PopoverTrigger, PopoverContent, Textarea } from '@djangocfg/ui';
import { Radio, Plus, Trash2, MessageSquare, Send } from 'lucide-react';
import { useCentrifugoLiveTestingContext } from '@/contexts/centrifugo';

export const LiveSubscriptionManager: React.FC = () => {
  const { subscriptions, subscribe, unsubscribe, unsubscribeAll, publish, isConnected } = useCentrifugoLiveTestingContext();
  const [newChannel, setNewChannel] = useState('');
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [publishingChannel, setPublishingChannel] = useState<string | null>(null);
  const [publishData, setPublishData] = useState<Record<string, string>>({});

  const handleSubscribe = async () => {
    if (!newChannel.trim()) return;

    setIsSubscribing(true);
    try {
      await subscribe(newChannel.trim());
      setNewChannel('');
    } catch (error) {
      console.error('Failed to subscribe:', error);
    } finally {
      setIsSubscribing(false);
    }
  };

  const handleUnsubscribe = (channel: string) => {
    unsubscribe(channel);
  };

  const handleQuickPublish = async (channel: string) => {
    const data = publishData[channel] || '';
    if (!data.trim()) return;

    setPublishingChannel(channel);
    try {
      let parsedData: any;
      try {
        // Try to parse as JSON
        parsedData = JSON.parse(data);
      } catch {
        // If not JSON, send as string
        parsedData = data;
      }

      await publish(channel, parsedData);

      // Clear input after successful publish
      setPublishData((prev) => ({ ...prev, [channel]: '' }));
    } catch (error) {
      console.error('Failed to publish:', error);
    } finally {
      setPublishingChannel(null);
    }
  };

  const subscriptionArray = Array.from(subscriptions.values());

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="h-5 w-5 text-blue-500" />
            <CardTitle>Active Subscriptions</CardTitle>
            <Badge variant="outline">{subscriptionArray.length} channels</Badge>
          </div>
          {subscriptionArray.length > 0 && (
            <Button variant="outline" size="sm" onClick={unsubscribeAll}>
              <Trash2 className="h-4 w-4 mr-2" />
              Unsubscribe All
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Subscribe to new channel */}
        <div className="flex gap-2 mb-4">
          <Input
            placeholder="Channel name (e.g., user#123, team#dev)"
            value={newChannel}
            onChange={(e) => setNewChannel(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !isSubscribing) {
                handleSubscribe();
              }
            }}
            disabled={!isConnected || isSubscribing}
            className="flex-1"
          />
          <Button
            onClick={handleSubscribe}
            disabled={!isConnected || isSubscribing || !newChannel.trim()}
            size="sm"
          >
            <Plus className="h-4 w-4 mr-2" />
            Subscribe
          </Button>
        </div>

        {!isConnected && (
          <div className="flex items-center justify-center p-6 text-muted-foreground text-sm bg-muted/20 rounded border border-border">
            <Radio className="h-8 w-8 mr-2 opacity-20" />
            <p>Connect to Centrifugo to manage subscriptions</p>
          </div>
        )}

        {isConnected && subscriptionArray.length === 0 && (
          <div className="flex items-center justify-center p-6 text-muted-foreground text-sm bg-muted/20 rounded border border-border">
            <MessageSquare className="h-8 w-8 mr-2 opacity-20" />
            <p>No active subscriptions. Subscribe to a channel to start receiving messages.</p>
          </div>
        )}

        {subscriptionArray.length > 0 && (
          <div className="space-y-2">
            {subscriptionArray.map((sub) => (
              <div
                key={sub.channel}
                className="flex items-center justify-between p-3 rounded border border-border bg-background/50 hover:bg-background transition-colors"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <Radio className="h-4 w-4 text-green-500 flex-shrink-0 animate-pulse" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <code className="text-sm font-mono font-semibold truncate">{sub.channel}</code>
                      <Badge variant="outline" className="text-xs flex-shrink-0">
                        {sub.messageCount} {sub.messageCount === 1 ? 'message' : 'messages'}
                      </Badge>
                    </div>
                    {sub.lastMessage && (
                      <p className="text-xs text-muted-foreground truncate">
                        Last: {typeof sub.lastMessage === 'string' ? sub.lastMessage : JSON.stringify(sub.lastMessage).slice(0, 50)}...
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {/* Quick Publish Popover */}
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <Send className="h-4 w-4" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80">
                      <div className="space-y-3">
                        <div>
                          <h4 className="font-semibold text-sm mb-1">Quick Publish</h4>
                          <p className="text-xs text-muted-foreground">
                            Send a message to <code className="text-xs">{sub.channel}</code>
                          </p>
                        </div>
                        <Textarea
                          placeholder='{"type": "notification", "message": "Hello!"}'
                          value={publishData[sub.channel] || ''}
                          onChange={(e) =>
                            setPublishData((prev) => ({ ...prev, [sub.channel]: e.target.value }))
                          }
                          rows={4}
                          className="font-mono text-xs"
                        />
                        <Button
                          onClick={() => handleQuickPublish(sub.channel)}
                          disabled={
                            !publishData[sub.channel]?.trim() || publishingChannel === sub.channel
                          }
                          className="w-full"
                          size="sm"
                        >
                          <Send className="h-4 w-4 mr-2" />
                          {publishingChannel === sub.channel ? 'Sending...' : 'Send Message'}
                        </Button>
                      </div>
                    </PopoverContent>
                  </Popover>

                  {/* Unsubscribe */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleUnsubscribe(sub.channel)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
