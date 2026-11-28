export function TLDR({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/30 p-4 mb-6 text-sm">
      <strong className="text-blue-700 dark:text-blue-400">TL;DR</strong>
      <div className="mt-1">{children}</div>
    </div>
  );
}
