import * as React from 'react';

export type QRCodeLevel = 'L' | 'M' | 'Q' | 'H';

export interface QRCodeCanvasOpts {
  errorCorrectionLevel: QRCodeLevel;
  type?: 'image/png' | 'image/jpeg' | 'image/webp';
  quality?: number;
  margin?: number;
  color?: {
    dark: string;
    light: string;
  };
  width?: number;
  rendererOpts?: {
    quality?: number;
  };
}

export interface StoreState {
  dataUrl: string | null;
  svgString: string | null;
  isGenerating: boolean;
  error: Error | null;
  generationKey: string;
}

export interface Store {
  subscribe: (callback: () => void) => () => void;
  getState: () => StoreState;
  setState: <K extends keyof StoreState>(key: K, value: StoreState[K]) => void;
  setStates: (updates: Partial<StoreState>) => void;
  notify: () => void;
}

export interface QRCodeContextValue {
  value: string;
  size: number;
  margin: number;
  level: QRCodeLevel;
  backgroundColor: string;
  foregroundColor: string;
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
}

export interface QRCodeProps extends Omit<React.ComponentProps<'div'>, 'onError'> {
  value: string;
  size?: number;
  level?: QRCodeLevel;
  margin?: number;
  quality?: number;
  backgroundColor?: string;
  foregroundColor?: string;
  onError?: (error: Error) => void;
  onGenerated?: () => void;
  asChild?: boolean;
}
