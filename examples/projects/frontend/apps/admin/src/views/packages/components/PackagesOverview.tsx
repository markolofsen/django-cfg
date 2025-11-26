import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@djangocfg/ui';
import { Package } from 'lucide-react';
import { PackageCard } from './PackageCard';
import { packages, categories, getPackagesByCategory } from '../packages';

export function PackagesOverview() {
  return (
    <section className="py-12 lg:py-20">
      <div className="container mx-auto px-4 sm:px-6">
        <div className="max-w-3xl mx-auto text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            <Package className="h-4 w-4" />
            <span>@djangocfg Ecosystem</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight">
            Monorepo Packages
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A complete ecosystem of packages for building modern Django + Next.js applications.
            Published to npm under <code className="text-primary">@djangocfg</code> scope.
          </p>
        </div>

        <Tabs defaultValue="all" className="w-full">
          <TabsList className="flex flex-wrap justify-center mb-8 bg-transparent gap-2">
            {categories.map((cat) => (
              <TabsTrigger
                key={cat.value}
                value={cat.value}
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              >
                {cat.label}
                <span className="ml-1.5 text-xs opacity-70">({cat.count})</span>
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="all">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {packages.map((pkg) => (
                <PackageCard key={pkg.name} {...pkg} />
              ))}
            </div>
          </TabsContent>

          {(['ui', 'utility', 'realtime', 'config'] as const).map((category) => (
            <TabsContent key={category} value={category}>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {getPackagesByCategory(category).map((pkg) => (
                  <PackageCard key={pkg.name} {...pkg} />
                ))}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </section>
  );
}
