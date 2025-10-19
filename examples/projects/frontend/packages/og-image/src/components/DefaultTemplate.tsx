/**
 * Default OG Image Template
 *
 * A modern, gradient-based template for OG images
 */

import type { ReactElement } from 'react';

import type { OgImageTemplateProps } from '../handler/types';

/**
 * Default OG Image Template Component
 *
 * Features:
 * - Modern gradient background
 * - Responsive text sizing
 * - Optional logo and site name
 * - Clean typography
 *
 * @param props - Template props with title, description, siteName, logo
 */
export function DefaultTemplate({
  title,
  description,
  siteName,
  logo,
}: OgImageTemplateProps): ReactElement {
  return (
    <div
      style={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '80px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
      }}
    >
      {/* Header with logo and site name */}
      {(logo || siteName) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
          }}
        >
          {logo && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={logo}
              alt="Logo"
              width={48}
              height={48}
              style={{
                borderRadius: '8px',
              }}
            />
          )}
          {siteName && (
            <div
              style={{
                fontSize: 28,
                fontWeight: 600,
                color: 'rgba(255, 255, 255, 0.95)',
                letterSpacing: '-0.02em',
              }}
            >
              {siteName}
            </div>
          )}
        </div>
      )}

      {/* Main content */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          flex: 1,
          justifyContent: 'center',
        }}
      >
        {/* Title */}
        <div
          style={{
            fontSize: title.length > 60 ? 56 : 72,
            fontWeight: 800,
            color: 'white',
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            textShadow: '0 2px 20px rgba(0, 0, 0, 0.2)',
            maxWidth: '100%',
            wordWrap: 'break-word',
          }}
        >
          {title}
        </div>

        {/* Description */}
        {description && (
          <div
            style={{
              fontSize: 32,
              fontWeight: 400,
              color: 'rgba(255, 255, 255, 0.85)',
              lineHeight: 1.5,
              letterSpacing: '-0.01em',
              maxWidth: '90%',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {description}
          </div>
        )}
      </div>

      {/* Footer decoration */}
      <div
        style={{
          display: 'flex',
          width: '100%',
          height: '4px',
          background: 'rgba(255, 255, 255, 0.3)',
          borderRadius: '2px',
        }}
      />
    </div>
  );
}

/**
 * Simple light template variant
 */
export function LightTemplate({
  title,
  description,
  siteName,
  logo,
}: OgImageTemplateProps): ReactElement {
  return (
    <div
      style={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        background: '#ffffff',
        padding: '80px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
      }}
    >
      {/* Header with logo and site name */}
      {(logo || siteName) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
          }}
        >
          {logo && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={logo}
              alt="Logo"
              width={48}
              height={48}
              style={{
                borderRadius: '8px',
              }}
            />
          )}
          {siteName && (
            <div
              style={{
                fontSize: 28,
                fontWeight: 600,
                color: '#111',
                letterSpacing: '-0.02em',
              }}
            >
              {siteName}
            </div>
          )}
        </div>
      )}

      {/* Main content */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          flex: 1,
          justifyContent: 'center',
        }}
      >
        {/* Title */}
        <div
          style={{
            fontSize: title.length > 60 ? 56 : 72,
            fontWeight: 800,
            color: '#111',
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            maxWidth: '100%',
            wordWrap: 'break-word',
          }}
        >
          {title}
        </div>

        {/* Description */}
        {description && (
          <div
            style={{
              fontSize: 32,
              fontWeight: 400,
              color: '#666',
              lineHeight: 1.5,
              letterSpacing: '-0.01em',
              maxWidth: '90%',
            }}
          >
            {description}
          </div>
        )}
      </div>

      {/* Footer decoration */}
      <div
        style={{
          display: 'flex',
          width: '100%',
          height: '4px',
          background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '2px',
        }}
      />
    </div>
  );
}
