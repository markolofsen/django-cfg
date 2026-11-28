# useTouchSafeStyle

**iOS WebKit auto-zoom prevention hook**

Returns touch-safe font-size for input/textarea elements to prevent iOS Safari/Chrome from zooming viewport on focus.

---

## Problem

iOS WebKit (Safari, Chrome, Edge) automatically zooms the viewport when an `<input>` or `<textarea>` with `font-size < 16px` receives focus. This causes:

- **UI "flying away"** — the entire page zooms in, scrolling content out of view
- **Critical UX failure** — especially in chat/conversation interfaces where context is essential
- **Disorientation** — users must manually zoom out to regain context

**Root Cause**: iOS design decision to help users read small text, but problematic for modern responsive designs.

---

## Solution

Use `max(16px, 1em)` to maintain relative sizing while preventing zoom:

- **16px**: iOS zoom threshold (anything ≥16px prevents auto-zoom)
- **1em**: Maintains relative sizing for accessibility (respects user's base font-size preference)
- **max()**: Takes the larger value, ensuring both goals are met

**Default Behavior**: iOS-only targeting. Android and desktop remain unaffected.

---

## API

```typescript
function useTouchSafeStyle(options?: TouchSafeStyleOptions): string | undefined
```

### Options

```typescript
interface TouchSafeStyleOptions {
  /** Target iOS specifically (default: true) */
  ios?: boolean;
  
  /** Target all mobile devices (default: false) */
  mobile?: boolean;
  
  /** Minimum font size to prevent zoom (default: '16px') */
  minSize?: string;
}
```

### Returns

- **iOS** (when `ios: true`, default): `"max(16px, 1em)"`
- **Android** (when `ios: true`): `undefined` (keeps optimal font-size, no zoom issue)
- **Desktop**: `undefined` (no mobile zoom behavior)
- **All mobile** (when `mobile: true`): `"max(16px, 1em)"` for iOS + Android

---

## Usage

### Basic (iOS-only, recommended)

```tsx
import { useTouchSafeStyle } from '@djangocfg/ui-core/hooks/device';

function ChatInput() {
  const fontSize = useTouchSafeStyle();
  
  return (
    <textarea
      style={{ fontSize }}
      placeholder="Type a message..."
    />
  );
}
```

**Result**:
- **iOS**: `font-size: max(16px, 1em)` — no zoom ✅
- **Android**: no inline style — keeps design's 14px ✅
- **Desktop**: no inline style — normal sizing ✅

### All Mobile Devices

```tsx
const fontSize = useTouchSafeStyle({ mobile: true, ios: false });

// iOS + Android both get 16px minimum
// Useful when: consistency across mobile platforms > optimal Android UX
```

### Custom Minimum Size

```tsx
const fontSize = useTouchSafeStyle({ minSize: '18px' });

// Ensures font-size ≥18px on iOS
// Useful for: accessibility requirements, larger touch targets
```

### Conditional Fallback

```tsx
function SearchInput() {
  const touchSafeFontSize = useTouchSafeStyle();
  
  return (
    <input
      type="search"
      style={{
        fontSize: touchSafeFontSize || '14px', // Desktop gets 14px
      }}
    />
  );
}
```

### Form with Multiple Inputs

```tsx
function LoginForm() {
  const fontSize = useTouchSafeStyle();
  
  return (
    <form>
      <input type="email" style={{ fontSize }} />
      <input type="password" style={{ fontSize }} />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

---

## CSS Alternative

For inputs that don't need programmatic control, use CSS utilities:

```tsx
import '@djangocfg/ui-core/styles';

// Option 1: Utility class (opt-in)
<div className="touch-safe-input">
  <input type="text" />
  <textarea />
</div>

// Option 2: Automatic via @supports (iOS detection at build time)
// Already applied globally — inputs get max(16px, 1em) on iOS
// No class needed, works without JS
```

**When to use CSS vs Hook**:
- **CSS**: Static inputs, no conditional logic, works without JS
- **Hook**: Dynamic styling, iOS-only precision, React-controlled components

---

## Why iOS-Only by Default?

**Android doesn't have auto-zoom behavior** — enforcing 16px there is unnecessary:

- ✅ **Better UX**: Android keeps design's optimal font-size (e.g., 14px for compact UI)
- ✅ **Precise targeting**: Only fixes the platform with the problem
- ✅ **Design flexibility**: Developers can choose smaller fonts on Android

**When to use `mobile: true`**:
- Consistent font-size across all mobile platforms is a requirement
- Simplicity over optimization
- Accessibility guidelines mandate 16px minimum everywhere

---

## WCAG Compliance

✅ **WCAG 2.1 Level AA Compliant**

- **SC 1.4.4 Resize Text**: Text can be resized up to 200% without loss of content or functionality
  - ✅ No viewport restrictions (no `user-scalable=no`)
  - ✅ `max(16px, 1em)` respects user's base font-size settings
  - ✅ Browser's text zoom still works

- **SC 1.4.10 Reflow**: Content reflows at 400% zoom without horizontal scrolling
  - ✅ Relative `em` units maintain reflow behavior
  - ✅ No fixed pixel-only sizing

**Rejected Alternative**: `viewport meta` with `user-scalable=no` ❌
```html
<!-- ❌ WCAG violation — prevents text zoom -->
<meta name="viewport" content="user-scalable=no" />
```

---

## Examples

### Chat Composer (Critical Context)

```tsx
function ChatComposer() {
  const fontSize = useTouchSafeStyle(); // iOS-only
  
  return (
    <textarea
      style={{ fontSize }}
      placeholder="Type your message..."
      aria-label="Message input"
    />
  );
}
```

**Rationale**: Chat conversations are context-critical. iOS zoom breaks UX entirely. Android keeps optimal 14px.

### Search Box (Optional Enhancement)

```tsx
function SearchBar() {
  const fontSize = useTouchSafeStyle();
  
  return (
    <input
      type="search"
      style={{ fontSize: fontSize || '15px' }} // Desktop: 15px
    />
  );
}
```

**Rationale**: Search is less context-critical, but preventing zoom improves UX. Desktop gets design's preferred size.

### Login Form (Security-Critical)

```tsx
function PasswordField() {
  const fontSize = useTouchSafeStyle({ mobile: true }); // All mobile
  
  return (
    <input
      type="password"
      style={{ fontSize }}
      autoComplete="current-password"
    />
  );
}
```

**Rationale**: Password fields benefit from larger text on all mobile devices for security/visibility.

---

## Implementation Details

### How It Works

```typescript
export function useTouchSafeStyle(options = {}) {
  const { isIOS, isMobile } = useDeviceDetect();
  const minSize = options.minSize || '16px';
  
  // All mobile (iOS + Android)
  if (options.mobile && isMobile) {
    return `max(${minSize}, 1em)`;
  }
  
  // iOS-only (default)
  if (options.ios !== false && isIOS) {
    return `max(${minSize}, 1em)`;
  }
  
  // Desktop or non-targeted mobile
  return undefined;
}
```

### Detection Method

Uses `useDeviceDetect()` hook (from `react-device-detect`):
- **iOS**: Detects iOS Safari, Chrome, Edge, Firefox
- **Android**: Detects Android browsers
- **Desktop**: Excludes non-mobile devices
- **SSR-safe**: Returns default values server-side, updates client-side

### Performance

- **Zero runtime cost on desktop** — returns `undefined`, no style applied
- **Minimal on mobile** — one device detect call (cached), simple string return
- **No layout shift** — applied on mount, before first paint

---

## Related

- **CSS Utilities**: `@djangocfg/ui-core/styles/utilities/touch-safe.css`
- **Research**: `@dev/research/ios-webkit-auto-zoom/`
- **Widget Implementation**: `@djangocfg/widget-chat` (auto-applied)
- **Device Detection**: `useDeviceDetect()` hook

---

## References

- [Apple: Configuring the Viewport](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/AdjustingtheTextSize/AdjustingtheTextSize.html)
- [MDN: viewport meta tag](https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag)
- [WCAG 2.1: Success Criterion 1.4.4](https://www.w3.org/WAI/WCAG21/Understanding/resize-text.html)
- [WCAG 2.1: Success Criterion 1.4.10](https://www.w3.org/WAI/WCAG21/Understanding/reflow.html)

---

## Migration from Viewport Meta

**Before** (❌ WCAG violation):
```tsx
// layout.tsx
export const viewport = {
  maximumScale: 1,
  userScalable: false, // ❌ Prevents text zoom
};
```

**After** (✅ WCAG compliant):
```tsx
// Remove viewport restrictions entirely
// Use useTouchSafeStyle() in components instead

function MyInput() {
  const fontSize = useTouchSafeStyle();
  return <input style={{ fontSize }} />;
}
```

**Benefits**:
- ✅ WCAG 2.1 AA compliant
- ✅ Text zoom works
- ✅ No global viewport restrictions
- ✅ iOS-only targeting (better Android UX)
