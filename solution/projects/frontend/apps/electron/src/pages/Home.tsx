import { useState } from 'react';
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui-core';
import { Minus, Plus } from 'lucide-react';

export default function Home() {
  const [count, setCount] = useState(0);

  return (
    <div className="text-center space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-primary mb-4">
          Electron + React + Tailwind v4
        </h1>
        <p className="text-muted-foreground">
          Built with Electron Forge, Vite, TypeScript, and @djangocfg/ui-core
        </p>
      </div>

      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Counter Demo</CardTitle>
          <CardDescription>Test the ui-core components</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-6xl font-bold">{count}</p>
          <div className="flex gap-4 justify-center">
            <Button
              variant="destructive"
              onClick={() => setCount((c) => c - 1)}
              className="gap-2"
            >
              <Minus className="h-4 w-4" />
              Decrease
            </Button>
            <Button
              variant="default"
              onClick={() => setCount((c) => c + 1)}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Increase
            </Button>
          </div>
          <Button
            variant="outline"
            onClick={() => setCount(0)}
            className="w-full"
          >
            Reset
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
