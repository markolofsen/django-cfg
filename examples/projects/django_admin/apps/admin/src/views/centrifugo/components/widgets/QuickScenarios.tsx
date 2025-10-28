/**
 * Quick Test Scenarios Component
 *
 * Provides one-click test scenarios for Centrifugo
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge } from '@djangocfg/ui';
import { Play, Zap } from 'lucide-react';
import { useCentrifugoLiveTestingContext } from '@/contexts/centrifugo';

export const QuickScenarios: React.FC = () => {
  const { quickScenarios, runScenario, isConnected } = useCentrifugoLiveTestingContext();
  const [runningScenario, setRunningScenario] = useState<string | null>(null);

  const handleRunScenario = async (scenarioId: string) => {
    setRunningScenario(scenarioId);
    try {
      await runScenario(scenarioId);
    } catch (error) {
      console.error('Failed to run scenario:', error);
    } finally {
      setRunningScenario(null);
    }
  };

  const getColorClasses = (color: string) => {
    const colorMap: Record<string, { bg: string; border: string; icon: string; button: string }> = {
      blue: {
        bg: 'bg-blue-50 dark:bg-blue-950/20',
        border: 'border-blue-200 dark:border-blue-800',
        icon: 'text-blue-500',
        button: 'bg-blue-600 hover:bg-blue-700',
      },
      green: {
        bg: 'bg-green-50 dark:bg-green-950/20',
        border: 'border-green-200 dark:border-green-800',
        icon: 'text-green-500',
        button: 'bg-green-600 hover:bg-green-700',
      },
      orange: {
        bg: 'bg-orange-50 dark:bg-orange-950/20',
        border: 'border-orange-200 dark:border-orange-800',
        icon: 'text-orange-500',
        button: 'bg-orange-600 hover:bg-orange-700',
      },
      purple: {
        bg: 'bg-purple-50 dark:bg-purple-950/20',
        border: 'border-purple-200 dark:border-purple-800',
        icon: 'text-purple-500',
        button: 'bg-purple-600 hover:bg-purple-700',
      },
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            <CardTitle>Quick Test Scenarios</CardTitle>
          </div>
          {isConnected && (
            <Badge variant="outline" className="bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800">
              Connected
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">
          One-click test scenarios that automatically connect, subscribe, and publish test messages.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickScenarios.map((scenario) => {
            const colors = getColorClasses(scenario.color);
            const isRunning = runningScenario === scenario.id;

            return (
              <Card key={scenario.id} className={`${colors.bg} border ${colors.border}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">{scenario.name}</h4>
                      <p className="text-xs text-muted-foreground">{scenario.description}</p>
                    </div>
                  </div>

                  <div className="bg-background/50 rounded p-2 mb-3 border border-border">
                    <code className="text-xs">
                      → Connect
                      <br />
                      → Subscribe to {scenario.channel}
                      <br />
                      → Publish message
                      <br />→ Receive immediately
                    </code>
                  </div>

                  <Button
                    onClick={() => handleRunScenario(scenario.id)}
                    disabled={isRunning}
                    className={`w-full ${colors.button} text-white`}
                    size="sm"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    {isRunning ? 'Running...' : 'Run Scenario'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
