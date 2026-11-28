import type { SVGProps } from 'react';

/**
 * The assistant's mark: a rounded tile with "A I" and a spark. It is drawn in `currentColor`, so it takes the colour of the place it sits in and follows the theme by itself
 * (white on the primary button, the foreground ink in the signed-out view and the greeting, in light and in dark). The spark carries `assistant-mark-spark`: the floating button twists it (`fab.css`). Size it with a class (`size-6`).
 */
export function AssistantMark(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 128 128" fill="currentColor" aria-hidden="true" focusable="false" {...props}>
      <path d="m49.7 43.72-12 37.44A1.39 1.39 0 0 0 39 83h3.36a1.39 1.39 0 0 0 1.33-1l1.88-6H62l-.23-.37L63.83 82a1.39 1.39 0 0 0 1.33 1h3.36a1.39 1.39 0 0 0 1.33-1.82l-12-37.44a1.4 1.4 0 0 0-1.33-1H51a1.39 1.39 0 0 0-1.3.98M47.57 70l6.19-19.27L60 70Z" />
      <rect width="6" height="40.24" x="79" y="42.75" rx="1.4" />
      <path d="M67.26 98h-29.1A8.16 8.16 0 0 1 30 89.84V38.16A8.16 8.16 0 0 1 38.16 30h51.68A8.16 8.16 0 0 1 98 38.16V64a2.07 2.07 0 0 0 2.12 2 11 11 0 0 1 4.91 1.14 2.06 2.06 0 0 0 3-1.87V38.16A18.16 18.16 0 0 0 89.84 20H38.16A18.16 18.16 0 0 0 20 38.16v51.68A18.16 18.16 0 0 0 38.16 108h33.3a2.07 2.07 0 0 0 1.47-3.53 16.1 16.1 0 0 1-3.71-5.06A2.11 2.11 0 0 0 67.26 98" />
      <path className="assistant-mark-spark" d="m111.73 101.8 9.06-3.57a1 1 0 0 0 0-1.86l-9.06-3.57a12.6 12.6 0 0 1-7.09-7.09l-3.57-9a1 1 0 0 0-.93-.63 1 1 0 0 0-.93.63l-3.57 9a12.58 12.58 0 0 1-7.09 7.09l-9 3.57a1 1 0 0 0 0 1.86l9 3.57a12.58 12.58 0 0 1 7.09 7.09l3.57 9a1 1 0 0 0 .93.64 1 1 0 0 0 .93-.64l3.57-9a12.6 12.6 0 0 1 7.09-7.09" />
    </svg>
  );
}
