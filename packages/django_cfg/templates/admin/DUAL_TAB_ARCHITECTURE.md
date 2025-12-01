# Dual-Tab Admin Architecture

This document explains the architecture and logic behind Django-CFG's dual-tab admin interface, which allows seamless integration of both built-in and external Next.js admin panels.

## Overview

Django-CFG admin interface supports **two independent Next.js admin panels** running side-by-side in separate tabs:

1. **Tab 1: Built-in Dashboard** - The default Next.js admin panel shipped with Django-CFG
2. **Tab 2: External Next.js Admin** - A custom Next.js admin panel from your solution project

Each tab operates independently with its own:
- Development server port
- Static file serving path
- Fallback mechanism
- iframe communication channel

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Django Admin Interface                      │
│  ┌───────────────────────────────┬───────────────────────────┐  │
│  │   Tab 1: Built-in Dashboard   │  Tab 2: External Admin    │  │
│  └───────────────────────────────┴───────────────────────────┘  │
│                                                                  │
│  Dev Mode:                      │  Dev Mode:                    │
│  ↓ http://localhost:3777/admin  │  ↓ http://localhost:3000/admin│
│                                                                  │
│  Fallback (Static):             │  Fallback (Static):           │
│  ↓ /cfg/admin/admin/            │  ↓ /cfg/nextjs-admin/admin/   │
└─────────────────────────────────────────────────────────────────┘
```

## Port Allocation

| Tab | Purpose | Dev Port | Static Path |
|-----|---------|----------|-------------|
| Tab 1 | Built-in Dashboard | `3777` | `/cfg/admin/admin/` |
| Tab 2 | External Next.js Admin | `3000` | `/cfg/nextjs-admin/admin/` |

### Why Different Ports?

Using separate ports prevents conflicts and allows both dev servers to run simultaneously:
- **Port 3777**: Reserved for Django-CFG's built-in admin panel
- **Port 3000**: Reserved for solution project's custom admin panel

## URL Resolution Logic

### Development Mode (DEBUG=True)

**Server-Side (Python)**: Always returns dev server URLs in DEBUG mode:

```python
def nextjs_admin_url(path=''):
    """Built-in Dashboard (Tab 1)"""
    if settings.DEBUG:
        return f'http://localhost:3777/admin/{path}'
    else:
        return f'/cfg/admin/admin/{path}'

def nextjs_external_admin_url(route=''):
    """External Next.js Admin (Tab 2)"""
    if settings.DEBUG:
        return f'http://localhost:3000/admin/{route}'
    else:
        return f'/cfg/nextjs-admin/admin/{route}'
```

**Client-Side (JavaScript)**: Verifies dev server availability before loading iframe:

```javascript
async function checkDevServerAvailable(url, retries = 3, timeout = 1000) {
    // Tries to fetch dev server with exponential backoff
    // - Attempt 1: immediate
    // - Attempt 2: +500ms delay
    // - Attempt 3: +1000ms delay
    // Total max: ~3.5s
}
```

**Why client-side checking?**
- Dev servers may be compiling on first request (cold start)
- Browser can handle CORS/network errors better than server-side sockets
- Allows retry with exponential backoff for slow Next.js compilation
- No server-side blocking during HTML rendering

### Production Mode (DEBUG=False)

In production, both tabs serve static files:
- Tab 1: Serves from `/cfg/admin/admin/` (built-in static files)
- Tab 2: Serves from `/cfg/nextjs-admin/admin/` (extracted from ZIP)

## Fallback Mechanism

Each iframe implements a smart fallback strategy when dev servers are unavailable:

```javascript
function handleLoadFailure() {
    if (!isDevMode) return; // Already using static files

    const originalSrc = iframe.getAttribute('data-original-src');
    const devUrl = new URL(originalSrc);
    const pathPart = devUrl.pathname.replace('/admin', '');

    // Determine correct fallback based on iframe ID
    let staticUrl;
    if (iframe.id === 'nextjs-dashboard-iframe-builtin') {
        staticUrl = `/cfg/admin/admin/${pathPart}`;
    } else if (iframe.id === 'nextjs-dashboard-iframe-nextjs') {
        staticUrl = `/cfg/nextjs-admin/admin/${pathPart}`;
    }

    iframe.src = staticUrl;
}
```

### Fallback Triggers

1. **Timeout**: 3 seconds without successful load
2. **Error Event**: iframe fails to load (network error, server down)
3. **Manual**: Dev server stopped during development

## iframe Communication

Each iframe maintains its own communication channel with the parent window using `postMessage`.

### Origin Detection

```javascript
// Get origin from data-original-src (not iframe.src, which may change)
const iframeSrc = iframe.getAttribute('data-original-src');
const iframeUrl = new URL(iframeSrc, window.location.origin);
const iframeOrigin = iframeUrl.origin;
```

**Why `data-original-src`?**
The `iframe.src` attribute may be changed by the fallback mechanism, so we use `data-original-src` to maintain the original intended origin for `postMessage` communication.

### Message Types

| Message Type | Direction | Purpose |
|--------------|-----------|---------|
| `parent-theme` | Parent → iframe | Sync theme (dark/light mode) |
| `parent-auth` | Parent → iframe | Inject JWT tokens |
| `iframe-ready` | iframe → Parent | iframe loaded and ready |
| `iframe-resize` | iframe → Parent | Update iframe height |
| `iframe-navigation` | iframe → Parent | Route change notification |
| `iframe-auth-status` | iframe → Parent | Authentication status |

## Tab Switching & State Reset

### Reset Logic

When switching tabs, the **previous** tab's iframe is reset to its initial URL:

```javascript
switchTab(tab) {
    if (this.previousTab !== tab) {
        // Reset iframe that was just hidden
        this.resetIframe(this.previousTab);
        this.previousTab = tab;
    }
    this.activeTab = tab;
}

resetIframe(tab) {
    const iframeId = tab === 'builtin'
        ? 'nextjs-dashboard-iframe-builtin'
        : 'nextjs-dashboard-iframe-nextjs';
    const iframe = document.getElementById(iframeId);

    if (iframe) {
        const originalSrc = iframe.getAttribute('data-original-src');
        iframe.src = originalSrc; // Reset to initial URL
    }
}
```

**Why Reset?**
This ensures that when users switch back to a tab, it starts from the home page rather than whatever route they navigated to previously.

### Open in New Window

The External Admin tab (Tab 2) includes an "Open in New Window" button that allows users to break out of the iframe and work in a dedicated browser window/tab:

```javascript
openInNewWindow() {
    // Get the current iframe URL for the External Admin tab
    const iframe = document.getElementById('nextjs-dashboard-iframe-nextjs');
    if (iframe) {
        const currentUrl = iframe.src || iframe.getAttribute('data-original-src');
        if (currentUrl) {
            window.open(currentUrl, '_blank', 'noopener,noreferrer');
        }
    }
}
```

**Features:**
- Only visible when External Admin tab is active (`x-show="activeTab === 'nextjs'"`)
- Opens current iframe URL in new window with `noopener,noreferrer` security flags
- Preserves current route via `postMessage` tracking (see below)
- Styled as action button with icon and text label

**How Route Tracking Works:**

In **production** (same-origin), `iframe.src` updates automatically:
```javascript
// iframe.src reflects current URL automatically
window.open(iframe.src, '_blank');
```

In **development** (cross-origin), we track navigation via `postMessage`:
```javascript
// iframe sends navigation events
case 'iframe-navigation':
    if (data?.path) {
        alpineData.currentNextjsPath = data.path;  // Track path
    }

// Button uses tracked path
openInNewWindow() {
    const url = new URL(baseUrl);
    url.pathname = this.currentNextjsPath;  // Apply tracked path
    window.open(url.toString(), '_blank');
}
```

**Why postMessage?**
Cross-origin iframes cannot access `iframe.src` due to browser security (CORS). The iframe must explicitly send navigation events via `postMessage`.

**Why This is Useful:**
- Full browser features (address bar, bookmarks, etc.)
- No iframe sandbox restrictions
- Easier debugging (browser DevTools)
- Better for complex workflows that require multiple windows
- Copy/paste and other browser features work better

## Static File Serving

### Built-in Admin (Tab 1)

**Location**: `django_cfg/static/frontend/admin/`

**Serving**:
- Development: `http://localhost:3777/admin`
- Production: `/cfg/admin/admin/` (Django `staticfiles`)

### External Admin (Tab 2)

**Source**: `{solution_project}/static/nextjs_admin.zip`

**Extraction**:
```python
# Target directory
base_dir = Path(settings.BASE_DIR) / 'static' / 'nextjs_admin'

# ZIP with metadata tracking
zip_path = Path(settings.BASE_DIR) / 'static' / 'nextjs_admin.zip'

# Automatic extraction with metadata comparison
extract_zip_if_needed(base_dir, zip_path, 'nextjs_admin')
```

**Serving**:
- Development: `http://localhost:3000/admin`
- Production: `/cfg/nextjs-admin/admin/` (Django serves extracted files)

### ZIP Extraction Logic

The system uses a **metadata marker file** (`.zip_meta`) to track ZIP state:

```python
# Metadata format: {size}:{mtime}
current_meta = f"{zip_stat.st_size}:{zip_stat.st_mtime}"

# Extraction triggers:
# 1. Directory doesn't exist → Extract
# 2. Marker file missing → Extract
# 3. ZIP metadata changed → Re-extract
# 4. Metadata matches → Use existing
```

**Why Metadata Comparison?**
More reliable than timestamp-only comparison, especially in Docker environments where file timestamps can be misleading.

## JWT Token Injection

Both tabs receive JWT tokens automatically for authenticated users:

```javascript
// Inject tokens into localStorage
localStorage.setItem('auth_token', '{access_token}');
localStorage.setItem('refresh_token', '{refresh_token}');
```

### Injection Strategy

1. **Server-Side**: Tokens injected into HTML response (see `views.py`)
2. **Client-Side**: Tokens sent via `postMessage` after iframe loads
3. **Storage**: Tokens stored in `localStorage` for Next.js apps

### Cache Control

HTML responses have aggressive cache-busting headers to ensure fresh token injection:

```python
response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
response['Pragma'] = 'no-cache'
response['Expires'] = '0'
```

## Configuration

### Django Config (solution project)

```python
from django_cfg import NextJsAdminConfig

config = DjangoConfig(
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin/apps/admin",
        api_output_path="app/_lib/api/generated",
        auto_build=True,
        # Optional overrides:
        # static_url="/cfg/nextjs-admin/",
        # dev_url="http://localhost:3000",
        # tab_title="Custom Admin",
    )
)
```

### Next.js Dev Servers

**Built-in Admin** (`django_admin/apps/admin/package.json`):
```json
{
  "scripts": {
    "dev": "next dev -p 3777"
  }
}
```

**External Admin** (solution project):
```json
{
  "scripts": {
    "dev": "next dev -p 3000"
  }
}
```

## Development Workflow

### Starting Both Dev Servers

```bash
# Terminal 1: Built-in admin
cd projects/django-cfg-dev/src/django_admin/apps/admin
pnpm dev  # Runs on port 3777

# Terminal 2: External admin
cd solution/projects/django_admin/apps/admin
pnpm dev  # Runs on port 3000

# Terminal 3: Django
cd solution/projects/django
python manage.py runserver
```

### Running Single Tab Only

You can run only one dev server - the other will fallback to static files:

```bash
# Only external admin in dev mode
cd solution/projects/django_admin/apps/admin
pnpm dev

# Built-in admin will fallback to /cfg/admin/admin/
```

## Template Tags Reference

### `{% nextjs_admin_url %}`
Returns URL for built-in dashboard (Tab 1)
- Dev: `http://localhost:3777/admin`
- Prod: `/cfg/admin/admin/`

### `{% nextjs_external_admin_url %}`
Returns URL for external admin (Tab 2)
- Dev: `http://localhost:3000/admin`
- Prod: `/cfg/nextjs-admin/admin/`

### `{% nextjs_external_admin_title %}`
Returns custom tab title from config (default: "Next.js Admin")

### `{% is_frontend_dev_mode %}`
Returns `True` if any dev server (port 3000 or 3777) is running

### `{% has_nextjs_external_admin %}`
Returns `True` if `NextJsAdminConfig` is configured

## Troubleshooting

### Tab shows wrong content

**Symptom**: Second tab shows content from first tab

**Cause**: `handleLoadFailure()` using wrong static URL

**Solution**: Check iframe ID in fallback logic (see `index.html:342-353`)

### postMessage origin mismatch

**Symptom**: Console error about mismatched origins

**Cause**: `iframeOrigin` determined from `iframe.src` after fallback changed it

**Solution**: Use `data-original-src` attribute instead (see `index.html:287`)

### Dev server not detected

**Symptom**: Tabs use static files despite dev server running

**Possible Causes**:
1. **Dev server still compiling**: Next.js cold start can take 1-2s
2. **Wrong port**: Dev server on different port than expected
3. **IPv6 vs IPv4**: Dev server listening only on IPv6 (`::1`)
4. **Firewall**: Connection blocked by firewall/antivirus
5. **Retry exhausted**: All 3 retry attempts failed

**Diagnostic Steps**:

1. **Check dev server is actually running**:
   ```bash
   lsof -i :3000 -i :3777 | grep LISTEN
   ```

2. **Test connection manually**:
   ```bash
   curl -I http://localhost:3000/admin
   curl -I http://localhost:3777/admin
   ```

3. **Check Django template tag logs** (add temporary logging):
   ```python
   # In django_cfg.py
   result = _is_port_available('localhost', 3000)
   print(f"[DEBUG] Port 3000 check: {result}")
   ```

4. **Increase retry attempts** (if dev server is very slow):
   ```python
   # Temporary test - increase retries
   _is_port_available('localhost', 3000, timeout=0.5, retries=5, retry_delay=0.1)
   ```

**Solutions**:
- **Wait for compilation**: Refresh page after 5-10 seconds
- **Verify port**: Check `package.json` scripts (`"dev": "next dev -p 3000"`)
- **Force IPv4**: Use `127.0.0.1` instead of `localhost`
- **Disable firewall**: Temporarily disable to test
- **Hard refresh**: Cmd+Shift+R to bypass browser cache

### Tokens not injected

**Symptom**: Next.js app shows "Not authenticated"

**Cause**:
1. User not logged in to Django
2. Cache returning 304 Not Modified
3. `postMessage` origin mismatch

**Solution**:
- Check Django session authentication
- Verify cache-control headers
- Check browser console for `postMessage` errors

## Performance Considerations

### Client-Side Dev Server Check

Port availability check happens in browser with exponential backoff:
```javascript
checkDevServerAvailable('http://localhost:3000', retries=3, timeout=1000)
```

**Impact per check**:
- **Best case**: ~0.1s (first fetch succeeds immediately)
- **Typical case**: ~0.5-1.5s (dev server compiling, succeeds on retry)
- **Worst case**: ~3.5s (all 3 attempts fail with delays: 1s + 0.5s + 1s + 1s)

**Retry schedule** (exponential backoff):
1. Attempt 1: immediate (0ms delay)
2. Attempt 2: +500ms delay
3. Attempt 3: +1000ms delay

**Why client-side checking?**
- ✅ Non-blocking: doesn't slow down server-side HTML rendering
- ✅ Better error handling: browser handles CORS/network errors gracefully
- ✅ User feedback: loading spinner shows progress
- ✅ Parallel loading: both iframe checks can run concurrently

### iframe Load Timeout

3-second timeout before fallback:
```javascript
loadTimeout = setTimeout(() => {
    handleLoadFailure();
}, 3000);
```

**Impact**: Users may see loading spinner for up to 3s if dev server is down

### Static File Caching

- **HTML**: No caching (`no-store, no-cache`)
- **Assets**: Standard browser caching (JS, CSS, images)

## Security Considerations

### iframe Sandbox

Both iframes use restrictive sandbox attributes:
```html
sandbox="allow-same-origin allow-scripts allow-forms
         allow-popups allow-modals
         allow-storage-access-by-user-activation"
```

**Warning**: Console will show "iframe can escape sandboxing" - this is expected because `allow-same-origin` + `allow-scripts` together allow sandbox escape.

### JWT Token Security

- Tokens injected via `postMessage` with origin validation
- Tokens stored in `localStorage` (accessible to Next.js apps)
- New tokens generated on each HTML page load
- Tokens cleared when Django session expires

### CORS & Origins

- Dev mode: Cross-origin iframes (`localhost:3777`, `localhost:3000`)
- Prod mode: Same-origin iframes (both served from Django domain)

## Future Enhancements

- [ ] Configurable port allocation per project
- [ ] Hot-reload coordination between Django and Next.js
- [ ] Shared state synchronization between tabs
- [ ] Tab-specific URL routing (preserve state across refreshes)
- [ ] WebSocket support for real-time updates
- [ ] SSO integration for external admin panels
- [ ] Health check dashboard for dev servers

---

**Last Updated**: 2025-10-29
**Django-CFG Version**: 2.x
**Next.js Version**: 15.x
