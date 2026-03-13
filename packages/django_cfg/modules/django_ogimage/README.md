# django_ogimage

Open Graph image generation for djangocfg. Renders 1200×630 PNG images using PicTex, caches them in `MEDIA_ROOT/ogimage/`.

No database, no models, no migrations — pure library.

---

## How it works

```
GET /og/<b64params>/
  → decode base64 → OGImageParams
  → check MEDIA_ROOT/ogimage/<key[:2]>/<key[2:4]>/<key>.png
  → HIT  → FileResponse
  → MISS → render(params) → save → FileResponse
```

Cache key = SHA256[:40] of stable params (everything except `page_url`). Same params always produce the same file — no redundant renders. Files are stored in a two-level sharded layout (like Git objects) to avoid inode limits.

---

## Setup

### 1. URLs

Registered automatically via `add_django_cfg_urls()`:

```python
# project/urls.py
from django_cfg import add_django_cfg_urls

urlpatterns = add_django_cfg_urls(urlpatterns)
# → GET /og/<b64params>/  (name: og-render)
```

### 2. Media

`MEDIA_ROOT` / `MEDIA_URL` are configured by djangocfg. The module writes to `MEDIA_ROOT/ogimage/` and media serving is handled by `add_django_cfg_urls()` automatically.

### 3. Renderer

Uses **PicTex** (`pictex>=2.1.0`) — supports gradients, RTL shaping, CJK fonts. PicTex is always available in `djangocfg[full]`.

---

## Usage

### Presets

Presets are frozen pydantic models with validated hex colors.

```python
from django_cfg.modules.django_ogimage import get_or_create_og_url, DARK_BLUE

url = get_or_create_og_url(DARK_BLUE.to_params(title="Hello", description="World"))

# With absolute URL
url = get_or_create_og_url(DARK_BLUE.to_params(title="Hello"), request=request)
```

Available dark presets: `DARK` · `DARK_BLUE` · `DARK_PURPLE` · `DARK_GREEN` · `DARK_ROSE`
Available light presets: `LIGHT` · `LIGHT_GRAY` · `LIGHT_WARM` · `LIGHT_GREEN`

```python
from django_cfg.modules.django_ogimage import get_preset, ALL

preset = get_preset("dark_blue")   # raises ValueError for unknown names
# ALL = {"dark": DARK, "dark_blue": DARK_BLUE, ...}
```

### Branding helper

`get_branded_og_url` adds a logo or built-in icon and a site name on top of any preset. `logo_url` takes priority over `icon`.

```python
from django_cfg.modules.django_ogimage import get_branded_og_url, DARK_BLUE, DEFAULT

params = DARK_BLUE.to_params(title="My Page", description="Subtitle")

# With site name only
url = get_branded_og_url(params, site_name="Acme Corp")

# With built-in Material icon
url = get_branded_og_url(params, icon="dashboard", site_name="Acme Corp")

# With external logo file
url = get_branded_og_url(params, logo_url="/path/to/logo.png", site_name="Acme Corp")

# Different layout preset
from django_cfg.modules.django_ogimage import HERO
url = get_branded_og_url(params, site_name="Acme", layout=HERO)

# Absolute URL
url = get_branded_og_url(params, site_name="Acme", request=request)
```

Cache key for `get_branded_og_url` = SHA256[:40] of `compute_cache_key(params) + json(logo_url, site_name, layout.name)`. Second call with the same inputs skips rendering entirely.

### Layout presets

Layout presets control where accent bar, brand overlay, and content are placed.

```python
from django_cfg.modules.django_ogimage import DEFAULT, HERO, ARTICLE, MINIMAL, get_layout

# DEFAULT  — accent top, brand bottom-left, content center (1200×630)
# HERO     — accent top, brand top-left, content bottom, larger title font
# ARTICLE  — no accent, brand top-left, content center, smaller title font
# MINIMAL  — no accent, no brand, content center

layout = get_layout("hero")   # raises ValueError for unknown names
```

### Built-in icons

10 SaaS-themed Material icons bundled as SVG files in `core/assets/icons/`:

```python
from django_cfg.modules.django_ogimage import list_icons, get_icon_path

icons = list_icons()           # sorted list of icon names without extension
path  = get_icon_path("dashboard")  # Path — raises ValueError if not found
```

Use `icon=` in `get_branded_og_url` to select a bundled icon by name. To update the bundled set, run `generate_icons.py`.

### Render PNG directly

```python
from django_cfg.modules.django_ogimage import render, OGImageParams
from django_cfg.modules.django_ogimage import DEFAULT

png_bytes = render(OGImageParams(title="Hello", style="light"))
png_bytes = render(OGImageParams(title="Hello"), layout=HERO, site_name="MySite")
```

### Build a shareable render URL

```python
from django_cfg.modules.django_ogimage import OGImageParams, build_og_url

params = OGImageParams(title="My Page", description="...", style="dark")
url = build_og_url(params, request=request)
# → https://example.com/og/eyJ0aXRsZSI6...
```

### In a serializer

```python
from django_cfg.modules.django_ogimage import get_branded_og_url, get_preset

class ArticleSerializer(serializers.ModelSerializer):
    og_image_url = serializers.SerializerMethodField()

    def get_og_image_url(self, obj):
        params = get_preset("dark_blue").to_params(title=obj.title, description=obj.excerpt)
        return get_branded_og_url(params, site_name="My Site", request=self.context.get("request"))
```

---

## OGImageParams fields

| Field | Default | Description |
|---|---|---|
| `title` | required | Main text (max 300 chars) |
| `description` | `""` | Subtitle (max 600 chars) |
| `locale` | `"en"` | BCP 47 locale — selects font |
| `style` | `"dark"` | `dark` or `light` |
| `bg_color` | `"#1a1a2e"` | Background color |
| `bg_color2` | `"#16213e"` | Gradient / secondary color |
| `text_color` | `"#ffffff"` | Text color |
| `accent_color` | `"#3b82f6"` | Accent / highlight color |
| `size` | `"1200x630"` | Output size |
| `page_url` | `""` | Source URL — excluded from cache key |

---

## Configuration

Environment variables (all optional):

| Variable | Default | Description |
|---|---|---|
| `OGIMAGE__MEDIA_SUBDIR` | `ogimage` | Subdirectory inside `MEDIA_ROOT` |
| `OGIMAGE__CACHE_ENABLED` | `true` | `false` to always re-render (dev) |
| `DJANGO_CFG_FONTS_DIR` | `~/.cache/django_cfg/fonts/` | Directory where fonts are downloaded |

---

## Locales & fonts

No fonts are bundled with the package. Fonts are downloaded on first use and cached locally.

| Locale | Font | Download size |
|---|---|---|
| `en`, `*` | Inter (variable TTF) | ~350 KB |
| `ko` | Noto Sans KR | ~3.5 MB |
| `ja` | Noto Sans JP | ~4.2 MB |
| `zh` | Noto Sans SC | ~6.5 MB |
| `ar` | Noto Sans Arabic (RTL) | ~300 KB |
| `he` | Noto Sans Hebrew (RTL) | ~200 KB |

At Django startup all fonts begin downloading in background daemon threads — they are ready by the time the first request arrives. If a font download fails, the default system font is used as fallback (no error raised).

To update font URLs edit `core/font_sources.py`.

---

## Sizes

`1200x630` (default) · `1200x600` · `800x418` · `1200x1200`

---

## Module layout

```
django_ogimage/
├── core/
│   ├── params.py          # OGImageParams + compute_cache_key()
│   ├── renderer.py        # render() — PicTex, decomposed into element builders
│   ├── layout.py          # OGLayoutPreset + DEFAULT/HERO/ARTICLE/MINIMAL + corner_to_fixed_pos()
│   ├── branding.py        # get_branded_og_url() — logo/icon/site_name overlay with caching
│   ├── svg.py             # _is_svg(), _svg_to_png() — SVG rasterization via skia
│   ├── icon.py            # get_icon_path(), list_icons() — built-in icon registry
│   ├── service.py         # get_or_create_og_url()
│   ├── fonts.py           # locale → font mapping (lazy download)
│   ├── font_sources.py    # remote TTF URLs — edit here to update fonts
│   └── assets/
│       └── icons/         # bundled Material SVG icons
├── cache/
│   └── _config.py         # OGImageConfig (env-driven settings)
├── http/
│   ├── views.py           # OGImageRenderView (GET /og/<b64params>/)
│   ├── utils.py           # build_og_url()
│   └── urls.py            # urlpatterns
├── presets/
│   ├── _base.py           # OGImagePreset (pydantic v2, frozen)
│   ├── dark.py            # DARK, DARK_BLUE, DARK_PURPLE, DARK_GREEN, DARK_ROSE
│   ├── light.py           # LIGHT, LIGHT_GRAY, LIGHT_WARM, LIGHT_GREEN
│   └── utils.py           # build_preset()
└── tests/                 # 201 tests
```
