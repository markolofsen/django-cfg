import { SuperHero } from '@djangocfg/ui/blocks';
import { Globe } from 'lucide-react';
import { ProjectCard } from './ProjectCard';
import { projects, projectStats } from '../data';

export function ProjectsOverview() {
  return (
    <div className="min-h-screen">
      <SuperHero
        badge={{ icon: <Globe className="h-4 w-4" />, text: 'Powered by DjangoCFG' }}
        title="Production"
        titleGradient="Projects"
        subtitle="Real-world applications and platforms built with DjangoCFG framework. From API services to full-stack platforms."
        stats={[
          { number: `${projectStats.total}`, label: 'Projects' },
          { number: `${projectStats.production}`, label: 'Production' },
          { number: `${projectStats.apiPlatforms}`, label: 'API Platforms' },
          { number: `${projectStats.categories}`, label: 'Categories' },
        ]}
        backgroundVariant="waves"
        backgroundIntensity="subtle"
      />

      <section className="py-12 lg:py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <ProjectCard key={project.name} {...project} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
