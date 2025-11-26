import { PackagesOverview } from './components';

export default function PackagesView() {
  return (
    <div className="min-h-screen">
      <PackagesOverview />
    </div>
  );
}

// Re-export components for individual use
export { PackagesOverview } from './components';
export { PackageCard } from './components';
export type { PackageCardProps } from './components';
