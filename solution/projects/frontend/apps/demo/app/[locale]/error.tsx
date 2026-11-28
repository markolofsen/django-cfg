'use client';

export default function LocaleError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <section className="mx-auto flex max-w-xl flex-col items-center gap-4 px-4 py-24 text-center">
          <h1 className="text-2xl font-bold">Something went wrong</h1>
          <p className="text-sm text-muted-foreground">{error.message}</p>
          <button
            onClick={reset}
            className="rounded-full bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            Try again
          </button>
        </section>
      </body>
    </html>
  );
}
