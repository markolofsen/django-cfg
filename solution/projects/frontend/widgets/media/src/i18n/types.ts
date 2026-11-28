/**
 * The media package's copy schema. English is the schema of record: every
 * locale is typed against `MediaCopy`, so a missing key is a `tsc` error rather
 * than `undefined` rendered into a toolbar button.
 */
export interface MediaCopy {
  close: string;
  diagram: string;
  download: string;
  failedToLoad: string;
  fitToView: string;
  flipHorizontal: string;
  flipVertical: string;
  fullscreen: string;
  loading: string;
  next: string;
  noImage: string;
  previous: string;
  rotate: string;
  zoomIn: string;
  zoomOut: string;
}
