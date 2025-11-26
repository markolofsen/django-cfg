import { ProjectsOverview } from './components';

export default function ProjectsView() {
  return <ProjectsOverview />;
}

// Re-export components for individual use
export { ProjectsOverview } from './components';
export { ProjectCard } from './components';
export type { ProjectCardProps } from './components';
