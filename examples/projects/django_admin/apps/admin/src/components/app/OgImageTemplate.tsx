/**
 * Custom OG Image Template for Unrealon
 *
 * Modern gradient design matching the Unrealon brand
 */

import type { ReactElement } from 'react';
import type { OgImageTemplateProps } from '@djangocfg/og-image';

interface OgImageProps extends OgImageTemplateProps {
  /** Subtitle for the image (maps to description) */
  subtitle?: string;
}

/**
 * Unrealon-branded OG image template
 */
export function OgImageTemplate({
  title,
  description,
  subtitle,
  siteName,
  logo,
}: OgImageProps): ReactElement {
  // Use subtitle if provided, otherwise fall back to description
  const displaySubtitle = subtitle || description;

  return (
    <div
      style={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
        padding: '80px',
        fontFamily: 'Manrope, system-ui, -apple-system, sans-serif',
        position: 'relative',
      }}
    >
      {/* Background pattern */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.15) 0%, transparent 50%)',
          opacity: 0.8,
        }}
      />

      {/* Header with logo and site name */}
      {(logo || siteName) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            position: 'relative',
            zIndex: 10,
          }}
        >
          {logo && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={logo}
              alt="Logo"
              width={56}
              height={56}
              style={{
                borderRadius: '12px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
              }}
            />
          )}
          {siteName && (
            <div
              style={{
                fontSize: 32,
                fontWeight: 700,
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
          gap: '32px',
          flex: 1,
          justifyContent: 'center',
          position: 'relative',
          zIndex: 10,
          maxWidth: '100%',
        }}
      >
        {/* Title */}
        <div
          style={{
            fontSize: title.length > 50 ? 64 : 80,
            fontWeight: 800,
            color: 'white',
            lineHeight: 1.1,
            letterSpacing: '-0.04em',
            textShadow: '0 2px 30px rgba(0, 0, 0, 0.4)',
            maxWidth: '95%',
            wordWrap: 'break-word',
          }}
        >
          {title}
        </div>

        {/* Subtitle/Description */}
        {displaySubtitle && (
          <div
            style={{
              fontSize: 36,
              fontWeight: 500,
              color: 'rgba(226, 232, 240, 0.9)',
              lineHeight: 1.5,
              letterSpacing: '-0.015em',
              maxWidth: '85%',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {displaySubtitle}
          </div>
        )}
      </div>

      {/* Footer accent */}
      <div
        style={{
          display: 'flex',
          width: '100%',
          height: '6px',
          background: 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%)',
          borderRadius: '3px',
          position: 'relative',
          zIndex: 10,
          boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)',
        }}
      />
    </div>
  );
}
