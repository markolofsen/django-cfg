# OG Image Route Handler

⚠️ **IMPORTANT: RENAME `route.example.tsx` TO `route.tsx` TO ACTIVATE**

This is an example file. To use this OG image route handler:

## Setup Instructions

1. **Rename the file**: Rename `route.example.tsx` to `route.tsx`

2. **Update metadata configuration**: Update `app/_core/metadata.ts`:
   - Change `ogImageBaseUrl: 'https://djangocfg.com/api/og'` 
   - To `ogImageBaseUrl: '/api/og'` (use local route)
   - This enables OG image generation using this route handler

3. **Static Export Limitation**: This route will **NOT work** with static export builds (`output: 'export'`)
   - It requires a server runtime to generate dynamic OG images
   - For static builds, OG images must be pre-generated or use a different approach
   - The route is automatically excluded from static export by `createOgImageDynamicRoute`

⚠️ **DO NOT USE THIS ROUTE IN STATIC EXPORT MODE**

## How It Works

This route handler uses `/api/og/[data]` instead of `/api/og?data=...` to avoid Next.js stripping query parameters in internal requests. The `[data]` parameter contains base64-encoded JSON with all OG image parameters (title, description, styling options, etc.).

## Customization

You can customize the OG image appearance by modifying the `defaultProps` in `route.tsx`:

- Background: `backgroundType`, `gradientStart`, `gradientEnd`, `backgroundColor`
- Typography: `titleSize`, `titleWeight`, `titleColor`, `descriptionSize`, `descriptionColor`
- Layout: `padding`, `logoSize`, `siteNameSize`
- Visibility: `showLogo`, `showSiteName`

All these parameters can also be passed via URL in base64-encoded format.

