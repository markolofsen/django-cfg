'use client';

import { useEffect, useMemo, useState, useCallback } from 'react';

// Safe defaults for SSR
const defaultSelectors = {
  isMobile: false,
  isTablet: false,
  isDesktop: false,
  isBrowser: false,
  isMobileOnly: false,
  isSmartTV: false,
  isConsole: false,
  isWearable: false,
  isEmbedded: false,
  isAndroid: false,
  isIOS: false,
  isWindows: false,
  isMacOs: false,
  isWinPhone: false,
  isChrome: false,
  isFirefox: false,
  isSafari: false,
  isOpera: false,
  isIE: false,
  isEdge: false,
  isEdgeChromium: false,
  isLegacyEdge: false,
  isChromium: false,
  isMobileSafari: false,
  isYandex: false,
  isMIUI: false,
  isSamsungBrowser: false,
  isElectron: false,
  osVersion: 'unknown',
  osName: 'unknown',
  fullBrowserVersion: 'unknown',
  browserVersion: 'unknown',
  browserName: 'unknown',
  mobileVendor: 'unknown',
  mobileModel: 'unknown',
  engineName: 'unknown',
  engineVersion: 'unknown',
  getUA: '',
  deviceType: 'unknown',
  isIOS13: false,
  isIPad13: false,
  isIPhone13: false,
  isIPod13: false,
};

const defaultDeviceData = {
  deviceType: 'unknown',
  osName: 'unknown',
  osVersion: 'unknown',
  browserName: 'unknown',
  browserVersion: 'unknown',
  fullBrowserVersion: 'unknown',
  mobileVendor: 'unknown',
  mobileModel: 'unknown',
  engineName: 'unknown',
  engineVersion: 'unknown',
  getUA: '',
};

const defaultOrientation = {
  isPortrait: false,
  isLandscape: false,
  orientation: 'portrait' as 'portrait' | 'landscape',
};

interface DeviceInfo {
  selectors: typeof defaultSelectors;
  deviceData: typeof defaultDeviceData;
  orientation: {
    isPortrait: boolean;
    isLandscape: boolean;
    orientation: 'portrait' | 'landscape';
  };
}

/**
 * Device detection hook wrapper for react-device-detect
 *
 * Provides a convenient interface to access device information including:
 * - Device type (mobile, tablet, desktop, etc.)
 * - Browser information (name, version, etc.)
 * - OS information (name, version, etc.)
 * - Orientation (portrait/landscape)
 *
 * @param userAgent - Optional user agent string (useful for SSR)
 * @returns Device detection object with all available information
 *
 * @example
 * ```tsx
 * const device = useDeviceDetect();
 *
 * if (device.isMobile) {
 *   return <MobileView />;
 * }
 *
 * return <DesktopView />;
 * ```
 */
export function useDeviceDetect(userAgent?: string) {
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>({
    selectors: defaultSelectors,
    deviceData: defaultDeviceData,
    orientation: defaultOrientation,
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Dynamic import to avoid SSR issues
    import('react-device-detect').then((deviceDetect) => {
      const ua = userAgent || window.navigator.userAgent;

      if (!ua) {
        console.warn('No user agent available');
        return;
      }

      const parsed = deviceDetect.parseUserAgent(ua);

      if (!parsed) {
        console.warn('Failed to parse user agent');
        return;
      }

      const selectors = deviceDetect.getSelectorsByUserAgent(ua) || defaultSelectors;

      const deviceData = {
        deviceType: parsed.device?.type || 'unknown',
        osName: parsed.os?.name || 'unknown',
        osVersion: parsed.os?.version || 'unknown',
        browserName: parsed.browser?.name || 'unknown',
        browserVersion: parsed.browser?.version || 'unknown',
        fullBrowserVersion: parsed.browser?.version || 'unknown',
        mobileVendor: parsed.device?.vendor || 'unknown',
        mobileModel: parsed.device?.model || 'unknown',
        engineName: parsed.engine?.name || 'unknown',
        engineVersion: parsed.engine?.version || 'unknown',
        getUA: parsed.ua || ua,
      };

      const isPortrait = window.innerHeight > window.innerWidth;
      const orientation = {
        isPortrait,
        isLandscape: !isPortrait,
        orientation: (isPortrait ? 'portrait' : 'landscape') as 'portrait' | 'landscape',
      };

      setDeviceInfo({ selectors, deviceData, orientation });
    }).catch((error) => {
      console.warn('Failed to load device detection:', error);
    });
  }, [userAgent]);

  // Update orientation on window resize
  const handleResize = useCallback(() => {
    const isPortrait = window.innerHeight > window.innerWidth;
    setDeviceInfo((prev) => ({
      ...prev,
      orientation: {
        isPortrait,
        isLandscape: !isPortrait,
        orientation: (isPortrait ? 'portrait' : 'landscape') as 'portrait' | 'landscape',
      },
    }));
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, [handleResize]);

  const { selectors, deviceData, orientation } = deviceInfo;

  return useMemo(() => ({
    // Device type selectors
    isMobile: selectors.isMobile ?? false,
    isTablet: selectors.isTablet ?? false,
    isDesktop: selectors.isDesktop ?? false,
    isBrowser: selectors.isBrowser ?? false,
    isMobileOnly: selectors.isMobileOnly ?? false,
    isSmartTV: selectors.isSmartTV ?? false,
    isConsole: selectors.isConsole ?? false,
    isWearable: selectors.isWearable ?? false,
    isEmbedded: selectors.isEmbedded ?? false,

    // OS selectors
    isAndroid: selectors.isAndroid ?? false,
    isIOS: selectors.isIOS ?? false,
    isWindows: selectors.isWindows ?? false,
    isMacOs: selectors.isMacOs ?? false,
    isWinPhone: selectors.isWinPhone ?? false,

    // Browser selectors
    isChrome: selectors.isChrome ?? false,
    isFirefox: selectors.isFirefox ?? false,
    isSafari: selectors.isSafari ?? false,
    isOpera: selectors.isOpera ?? false,
    isIE: selectors.isIE ?? false,
    isEdge: selectors.isEdge ?? false,
    isEdgeChromium: selectors.isEdgeChromium ?? false,
    isLegacyEdge: selectors.isLegacyEdge ?? false,
    isChromium: selectors.isChromium ?? false,
    isMobileSafari: selectors.isMobileSafari ?? false,
    isYandex: selectors.isYandex ?? false,
    isMIUI: selectors.isMIUI ?? false,
    isSamsungBrowser: selectors.isSamsungBrowser ?? false,
    isElectron: selectors.isElectron ?? false,

    // iOS version selectors
    isIOS13: selectors.isIOS13 ?? false,
    isIPad13: selectors.isIPad13 ?? false,
    isIPhone13: selectors.isIPhone13 ?? false,
    isIPod13: selectors.isIPod13 ?? false,

    // Device information
    deviceType: deviceData.deviceType ?? 'unknown',
    osName: deviceData.osName ?? 'unknown',
    osVersion: deviceData.osVersion ?? 'unknown',
    browserName: deviceData.browserName ?? 'unknown',
    browserVersion: deviceData.browserVersion ?? 'unknown',
    fullBrowserVersion: deviceData.fullBrowserVersion ?? 'unknown',
    mobileVendor: deviceData.mobileVendor ?? 'unknown',
    mobileModel: deviceData.mobileModel ?? 'unknown',
    engineName: deviceData.engineName ?? 'unknown',
    engineVersion: deviceData.engineVersion ?? 'unknown',
    getUA: deviceData.getUA ?? '',

    // Orientation
    isPortrait: orientation.isPortrait,
    isLandscape: orientation.isLandscape,
    orientation: orientation.orientation,

    // Raw data (for advanced usage)
    selectors,
    deviceData,
  }), [selectors, deviceData, orientation]);
}

export type DeviceDetectResult = ReturnType<typeof useDeviceDetect>;
