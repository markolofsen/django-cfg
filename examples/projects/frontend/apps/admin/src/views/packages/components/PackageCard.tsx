import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge } from '@djangocfg/ui';
import type { PackageInfo } from '../packages';
import { statusColors, categoryColors } from '../packages';

export interface PackageCardProps extends PackageInfo {}

export function PackageCard({
  name,
  description,
  icon: Icon,
  features,
  status,
  category,
  npmUrl,
}: PackageCardProps) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/50 h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
              <Icon className="h-5 w-5" />
            </div>
            <CardTitle className="text-lg font-mono">{name}</CardTitle>
          </div>
          <div className="flex gap-1.5">
            <Badge variant="outline" className={statusColors[status]}>
              {status}
            </Badge>
            <Badge variant="outline" className={categoryColors[category]}>
              {category}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        <CardDescription className="text-sm leading-relaxed mb-4">
          {description}
        </CardDescription>
        <div className="mt-auto">
          <div className="flex flex-wrap gap-1.5">
            {features.map((feature) => (
              <Badge key={feature} variant="secondary" className="text-xs">
                {feature}
              </Badge>
            ))}
          </div>
          {npmUrl && (
            <a
              href={npmUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-block text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View on npm →
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
