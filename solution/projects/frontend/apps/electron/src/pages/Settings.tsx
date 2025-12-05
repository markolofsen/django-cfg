import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Switch, Label, Button } from '@djangocfg/ui-core';
import { useTheme, Theme } from '@djangocfg/electron-ui';
import { Sun, Moon, Monitor } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';

interface SettingItemProps {
  id: string;
  title: string;
  description: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}

function SettingItem({ id, title, description, checked, onCheckedChange }: SettingItemProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="space-y-0.5">
        <Label htmlFor={id} className="text-base font-medium">
          {title}
        </Label>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
      />
    </div>
  );
}

const themeOptions: { value: Theme; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
];

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const [notifications, setNotifications] = useState(true);
  const [autoUpdate, setAutoUpdate] = useState(false);
  const [devTools, setDevTools] = useState(false);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Settings</h1>
        <p className="text-muted-foreground">Manage your application preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize how the app looks</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label className="text-base font-medium">Theme</Label>
            <p className="text-sm text-muted-foreground">Select your preferred theme</p>
            <div className="flex gap-2 mt-2">
              {themeOptions.map((option) => (
                <Button
                  key={option.value}
                  variant={theme === option.value ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setTheme(option.value)}
                  className={cn(
                    "flex-1 gap-2",
                    theme === option.value && "bg-primary/10 text-primary border-primary"
                  )}
                >
                  <option.icon className="h-4 w-4" />
                  {option.label}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>Configure notification preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingItem
            id="notifications"
            title="Desktop Notifications"
            description="Receive desktop notifications for important events"
            checked={notifications}
            onCheckedChange={setNotifications}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Updates</CardTitle>
          <CardDescription>Manage application updates</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingItem
            id="auto-update"
            title="Auto Update"
            description="Automatically check and install updates"
            checked={autoUpdate}
            onCheckedChange={setAutoUpdate}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Developer</CardTitle>
          <CardDescription>Advanced settings for developers</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <SettingItem
            id="dev-tools"
            title="Developer Tools"
            description="Enable developer tools and debugging features"
            checked={devTools}
            onCheckedChange={setDevTools}
          />
        </CardContent>
      </Card>
    </div>
  );
}
