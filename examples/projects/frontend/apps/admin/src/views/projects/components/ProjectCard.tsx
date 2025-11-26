import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge } from '@djangocfg/ui';
import { ExternalLink } from 'lucide-react';
import type { ProjectInfo } from '../data';
import { statusColors, categoryColors } from '../data';

export interface ProjectCardProps extends ProjectInfo {}

export function ProjectCard({
  name,
  url,
  description,
  icon: Icon,
  features,
  status,
  category,
}: ProjectCardProps) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="block h-full">
      <Card className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/50 h-full flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <CardTitle className="text-lg flex items-center gap-2">
                  {name}
                  <ExternalLink className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground" />
                </CardTitle>
                <span className="text-xs text-muted-foreground">{new URL(url).hostname}</span>
              </div>
            </div>
            <div className="flex gap-1.5 flex-wrap justify-end">
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
          </div>
        </CardContent>
      </Card>
    </a>
  );
}
