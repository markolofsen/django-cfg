'use client';

import { Slot as SlotPrimitive } from '@radix-ui/react-slot';
import * as React from 'react';
import { useComposedRefs } from '@djangocfg/ui-core/lib';
import { cn } from '@djangocfg/ui-core/lib';
import type { QRCodeProps, QRCodeContextValue, StoreState, Store, QRCodeCanvasOpts } from './types';

const ROOT_NAME = 'QRCode';
const CANVAS_NAME = 'QRCodeCanvas';
const SVG_NAME = 'QRCodeSvg';
const IMAGE_NAME = 'QRCodeImage';
const SKELETON_NAME = 'QRCodeSkeleton';

const StoreContext = React.createContext<Store | null>(null);

function useStore<T>(selector: (state: StoreState) => T): T {
  const store = React.useContext(StoreContext);
  if (!store) {
    throw new Error(`\`useQRCode\` must be used within \`${ROOT_NAME}\``);
  }

  const getSnapshot = React.useCallback(
    () => selector(store.getState()),
    [store, selector],
  );

  return React.useSyncExternalStore(store.subscribe, getSnapshot, getSnapshot);
}

const QRCodeContext = React.createContext<QRCodeContextValue | null>(null);

function useQRCodeContext(consumerName: string) {
  const context = React.useContext(QRCodeContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within \`${ROOT_NAME}\``);
  }
  return context;
}

function useLazyRef<T>(init: () => T): React.RefObject<T> {
  const ref = React.useRef<T | null>(null);
  if (ref.current === null) {
    ref.current = init();
  }
  return ref as React.RefObject<T>;
}

export function QRCode(props: QRCodeProps) {
  const {
    value,
    size = 200,
    level = 'M',
    margin = 1,
    quality = 0.92,
    backgroundColor = '#ffffff',
    foregroundColor = '#000000',
    onError,
    onGenerated,
    className,
    style,
    asChild,
    ...rootProps
  } = props;

  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  const listenersRef = useLazyRef(() => new Set<() => void>());
  const stateRef = useLazyRef<StoreState>(() => ({
    dataUrl: null,
    svgString: null,
    isGenerating: false,
    error: null,
    generationKey: '',
  }));

  const store = React.useMemo<Store>(() => {
    return {
      subscribe: (cb) => {
        listenersRef.current.add(cb);
        return () => listenersRef.current.delete(cb);
      },
      getState: () => stateRef.current,
      setState: (key, value) => {
        if (Object.is(stateRef.current[key], value)) return;
        stateRef.current[key] = value;
        store.notify();
      },
      setStates: (updates) => {
        let hasChanged = false;

        for (const key of Object.keys(updates) as Array<keyof StoreState>) {
          const value = updates[key];
          if (value !== undefined && !Object.is(stateRef.current[key], value)) {
            Object.assign(stateRef.current, { [key]: value });
            hasChanged = true;
          }
        }

        if (hasChanged) {
          store.notify();
        }
      },
      notify: () => {
        for (const cb of listenersRef.current) {
          cb();
        }
      },
    };
  }, [listenersRef, stateRef]);

  const canvasOpts = React.useMemo<QRCodeCanvasOpts>(
    () => ({
      errorCorrectionLevel: level,
      type: 'image/png',
      quality,
      margin,
      color: {
        dark: foregroundColor,
        light: backgroundColor,
      },
      width: size,
    }),
    [level, margin, foregroundColor, backgroundColor, size, quality],
  );

  const generationKey = React.useMemo(() => {
    if (!value) return '';

    return JSON.stringify({
      value,
      size,
      level,
      margin,
      quality,
      foregroundColor,
      backgroundColor,
    });
  }, [value, level, margin, foregroundColor, backgroundColor, size, quality]);

  const onQRCodeGenerate = React.useCallback(
    async (targetGenerationKey: string) => {
      if (!value || !targetGenerationKey) return;

      const currentState = store.getState();
      if (
        currentState.isGenerating ||
        currentState.generationKey === targetGenerationKey
      )
        return;

      store.setStates({
        isGenerating: true,
        error: null,
      });

      try {
        const QRCode = (await import('qrcode')).default;

        let dataUrl: string | null = null;

        try {
          dataUrl = await QRCode.toDataURL(value, canvasOpts as Parameters<typeof QRCode.toDataURL>[1]);
        } catch {
          dataUrl = null;
        }

        if (canvasRef.current) {
          const { type: _t, quality: _q, rendererOpts: _r, ...renderersOpts } = canvasOpts;
          void _t; void _q; void _r;
          await QRCode.toCanvas(canvasRef.current, value, renderersOpts);
        }

        const svgString = await QRCode.toString(value, {
          errorCorrectionLevel: canvasOpts.errorCorrectionLevel,
          margin: canvasOpts.margin,
          color: canvasOpts.color,
          width: canvasOpts.width,
          type: 'svg',
        });

        store.setStates({
          dataUrl,
          svgString,
          isGenerating: false,
          generationKey: targetGenerationKey,
        });

        onGenerated?.();
      } catch (error) {
        const parsedError =
          error instanceof Error
            ? error
            : new Error('Failed to generate QR code');
        store.setStates({
          error: parsedError,
          isGenerating: false,
        });
        onError?.(parsedError);
      }
    },
    [value, canvasOpts, store, onError, onGenerated],
  );

  const contextValue = React.useMemo<QRCodeContextValue>(
    () => ({
      value,
      size,
      level,
      margin,
      backgroundColor,
      foregroundColor,
      canvasRef,
    }),
    [value, size, backgroundColor, foregroundColor, level, margin],
  );

  React.useLayoutEffect(() => {
    if (generationKey) {
      const rafId = requestAnimationFrame(() => {
        onQRCodeGenerate(generationKey);
      });

      return () => cancelAnimationFrame(rafId);
    }
  }, [generationKey, onQRCodeGenerate]);

  const RootPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <StoreContext.Provider value={store}>
      <QRCodeContext.Provider value={contextValue}>
        <RootPrimitive
          data-slot="qr-code"
          {...rootProps}
          className={cn(className, 'relative flex flex-col items-center gap-2')}
          style={
            {
              '--qr-code-size': `${size}px`,
              ...style,
            } as React.CSSProperties
          }
        />
      </QRCodeContext.Provider>
    </StoreContext.Provider>
  );
}

QRCode.displayName = ROOT_NAME;

interface QRCodeCanvasProps extends React.ComponentProps<'canvas'> {
  asChild?: boolean;
}

export function QRCodeCanvas(props: QRCodeCanvasProps) {
  const { asChild, className, ref, ...canvasProps } = props;

  const context = useQRCodeContext(CANVAS_NAME);
  const generationKey = useStore((state) => state.generationKey);

  const composedRef = useComposedRefs(ref, context.canvasRef);

  const CanvasPrimitive = asChild ? SlotPrimitive : 'canvas';

  return (
    <CanvasPrimitive
      data-slot="qr-code-canvas"
      {...canvasProps}
      ref={composedRef}
      width={context.size}
      height={context.size}
      className={cn(
        'relative max-h-(--qr-code-size) max-w-(--qr-code-size)',
        !generationKey && 'invisible',
        className,
      )}
    />
  );
}

QRCodeCanvas.displayName = CANVAS_NAME;

interface QRCodeSvgProps extends React.ComponentProps<'div'> {
  asChild?: boolean;
}

export function QRCodeSvg(props: QRCodeSvgProps) {
  const { asChild, className, style, ...svgProps } = props;

  const context = useQRCodeContext(SVG_NAME);
  const svgString = useStore((state) => state.svgString);

  if (!svgString) return null;

  const SvgPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <SvgPrimitive
      data-slot="qr-code-svg"
      {...svgProps}
      className={cn(
        'relative max-h-(--qr-code-size) max-w-(--qr-code-size)',
        className,
      )}
      style={{ width: context.size, height: context.size, ...style }}
      dangerouslySetInnerHTML={{ __html: svgString }}
    />
  );
}

QRCodeSvg.displayName = SVG_NAME;

interface QRCodeImageProps extends React.ComponentProps<'img'> {
  asChild?: boolean;
}

export function QRCodeImage(props: QRCodeImageProps) {
  const { alt = 'QR Code', asChild, className, ...imageProps } = props;

  const context = useQRCodeContext(IMAGE_NAME);
  const dataUrl = useStore((state) => state.dataUrl);

  if (!dataUrl) return null;

  const ImagePrimitive = asChild ? SlotPrimitive : 'img';

  return (
    <ImagePrimitive
      data-slot="qr-code-image"
      {...imageProps}
      src={dataUrl}
      alt={alt}
      width={context.size}
      height={context.size}
      className={cn(
        'relative max-h-(--qr-code-size) max-w-(--qr-code-size)',
        className,
      )}
    />
  );
}

QRCodeImage.displayName = IMAGE_NAME;

interface QRCodeDownloadProps extends React.ComponentProps<'button'> {
  filename?: string;
  format?: 'png' | 'svg';
  asChild?: boolean;
}

export function QRCodeDownload(props: QRCodeDownloadProps) {
  const {
    filename = 'qrcode',
    format = 'png',
    asChild,
    className,
    children,
    ...buttonProps
  } = props;

  const dataUrl = useStore((state) => state.dataUrl);
  const svgString = useStore((state) => state.svgString);

  const onClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      buttonProps.onClick?.(event);
      if (event.defaultPrevented) return;

      const link = document.createElement('a');

      if (format === 'png' && dataUrl) {
        link.href = dataUrl;
        link.download = `${filename}.png`;
      } else if (format === 'svg' && svgString) {
        const blob = new Blob([svgString], { type: 'image/svg+xml' });
        link.href = URL.createObjectURL(blob);
        link.download = `${filename}.svg`;
      } else {
        return;
      }

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      if (format === 'svg' && svgString) {
        URL.revokeObjectURL(link.href);
      }
    },
    // The single handler, not the whole rest-props object: `buttonProps` is a
    // new reference every render, so depending on it would rebuild this
    // callback unconditionally.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [dataUrl, svgString, filename, format, buttonProps.onClick],
  );

  const ButtonPrimitive = asChild ? SlotPrimitive : 'button';

  return (
    <ButtonPrimitive
      type="button"
      data-slot="qr-code-download"
      {...buttonProps}
      className={cn('max-w-(--qr-code-size)', className)}
      onClick={onClick}
    >
      {children ?? `Download ${format.toUpperCase()}`}
    </ButtonPrimitive>
  );
}

QRCodeDownload.displayName = 'QRCodeDownload';

interface QRCodeOverlayProps extends React.ComponentProps<'div'> {
  asChild?: boolean;
}

export function QRCodeOverlay(props: QRCodeOverlayProps) {
  const { asChild, className, ...overlayProps } = props;

  const OverlayPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <OverlayPrimitive
      data-slot="qr-code-overlay"
      {...overlayProps}
      className={cn(
        'absolute top-1/2 left-1/2 flex -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-sm bg-background',
        className,
      )}
    />
  );
}

QRCodeOverlay.displayName = 'QRCodeOverlay';

interface QRCodeSkeletonProps extends React.ComponentProps<'div'> {
  asChild?: boolean;
}

export function QRCodeSkeleton(props: QRCodeSkeletonProps) {
  const { asChild, className, style, ...skeletonProps } = props;

  const context = useQRCodeContext(SKELETON_NAME);
  const dataUrl = useStore((state) => state.dataUrl);
  const svgString = useStore((state) => state.svgString);
  const generationKey = useStore((state) => state.generationKey);

  const isLoaded = dataUrl || svgString || generationKey;

  if (isLoaded) return null;

  const SkeletonPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <SkeletonPrimitive
      data-slot="qr-code-skeleton"
      {...skeletonProps}
      className={cn(
        'absolute max-h-(--qr-code-size) max-w-(--qr-code-size) animate-pulse bg-accent',
        className,
      )}
      style={{
        width: context.size,
        height: context.size,
        ...style,
      }}
    />
  );
}

QRCodeSkeleton.displayName = SKELETON_NAME;
