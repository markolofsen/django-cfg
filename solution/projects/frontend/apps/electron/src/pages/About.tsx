import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Separator, CopyButton } from '@djangocfg/ui-core';

interface InfoRowProps {
  label: string;
  value: string;
  badge?: boolean;
}

function InfoRow({ label, value, badge = false }: InfoRowProps) {
  return (
    <div className="flex justify-between items-center py-3">
      <span className="text-muted-foreground">{label}</span>
      {badge ? (
        <Badge variant="secondary">{value}</Badge>
      ) : (
        <span className="font-medium">{value}</span>
      )}
    </div>
  );
}

export default function About() {
  const version = '1.0.0';

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">About</h1>
        <p className="text-muted-foreground">Application information and stack details</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>DjangoCFG Desktop</CardTitle>
          <CardDescription>Cross-platform desktop application</CardDescription>
        </CardHeader>
        <CardContent className="space-y-0">
          <InfoRow label="Version" value={version} badge />
          <Separator />
          <InfoRow label="Framework" value="Electron" />
          <Separator />
          <InfoRow label="Build Tool" value="Electron Forge + Vite" />
          <Separator />
          <InfoRow label="UI Framework" value="React 19" />
          <Separator />
          <InfoRow label="UI Components" value="@djangocfg/ui-core" />
          <Separator />
          <InfoRow label="Styling" value="Tailwind CSS v4" />
          <Separator />
          <InfoRow label="Language" value="TypeScript" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Installation</CardTitle>
          <CardDescription>Use @djangocfg/ui-core in your Electron app</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 p-3 rounded-lg bg-muted font-mono text-sm">
            <code className="flex-1">pnpm add @djangocfg/ui-core</code>
            <CopyButton value="pnpm add @djangocfg/ui-core" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
