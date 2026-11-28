import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  LazyMapContainer,
  MapMarker,
  MapSource,
  MapLayer,
  MAP_STYLES,
  useMapImages,
  createSymbolLayer,
  MeasureControl,
  useGeolocation,
  DraggableMarkers,
  GeocoderInput,
  GeocoderControl,
  MapMarkers,
  MarkerCard,
} from '.';
import type { MapStyleKey, MarkerData, DraggablePoint, GeocodeResult, MarkerWithCard } from '.';

const BERLIN: MarkerData = {
  id: 'berlin',
  longitude: 13.405,
  latitude: 52.52,
  data: { label: 'Berlin DC' },
};

const meta = {
  title: 'Widgets/Map/Map',
  component: LazyMapContainer,
  // Tiles come from the network and the canvas needs WebGL; neither is there in a headless run.
  tags: ['autodocs', '!test'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'MapLibre GL map (lazy-loaded). By default `scrollProtection` is **on** — ' +
          'the wheel/trackpad will not zoom the map until you click into it, so an ' +
          'inline map embedded in a scrollable page (e.g. a chat transcript) never ' +
          'hijacks the page scroll. Click the map to interact, click outside or move ' +
          'the pointer away to re-lock. Pass `scrollProtection={false}` to opt out.',
      },
    },
  },
} satisfies Meta<typeof LazyMapContainer>;

export default meta;
type Story = StoryObj<typeof meta>;

const Frame = ({ children }: { children: React.ReactNode }) => (
  <div className="h-[360px] w-[560px] overflow-hidden rounded-xl border border-border">
    {children}
  </div>
);

/**
 * Default — scroll protection is on. Try scrolling over the map: the page
 * scrolls, the map does not zoom. Click the map first, then the wheel zooms.
 */
export const Default: Story = {
  render: () => (
    <Frame>
      <LazyMapContainer
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
      >
        <MapMarker marker={BERLIN} ariaLabel="Berlin DC" />
      </LazyMapContainer>
    </Frame>
  ),
};

/**
 * Scroll protection proves itself when the map sits inside a long,
 * scrollable page — scroll the column and the map stays put until clicked.
 */
export const InScrollablePage: Story = {
  name: 'In a scrollable page',
  render: () => (
    <div className="h-[420px] w-[560px] space-y-4 overflow-y-auto rounded-xl border border-border p-4">
      <p className="text-sm text-muted-foreground">
        Scroll this column — the wheel passes through the map below instead of
        zooming it. Click the map to interact.
      </p>
      <Frame>
        <LazyMapContainer
          initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
        >
          <MapMarker marker={BERLIN} ariaLabel="Berlin DC" />
        </LazyMapContainer>
      </Frame>
      <p className="text-sm text-muted-foreground">
        More content below so there is something to scroll into…
      </p>
      <div className="h-64 rounded-lg bg-muted/40" />
    </div>
  ),
};

/**
 * Opt out — `scrollProtection={false}` restores the classic behavior where
 * the wheel zooms the map immediately (use only for full-page maps).
 */
export const NoScrollProtection: Story = {
  name: 'Without scroll protection',
  render: () => (
    <Frame>
      <LazyMapContainer
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
        scrollProtection={false}
      >
        <MapMarker marker={BERLIN} ariaLabel="Berlin DC" />
      </LazyMapContainer>
    </Frame>
  ),
};

// A tiny 16×16 amber location-dot PNG (data-URL) so the story needs no
// network asset. Registered via `useMapImages`, then drawn by a symbol layer.
const PIN_ICON =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAhElEQVR42mNgGAWjgP7g/' +
  '38GBgaG/wwMDP8ZGBj+MzAw/GdgYPjPwMDwn4GB4T8DA8N/BgaG/wwMDP8ZGBj+MzAw/GdgYPjPwMDwn4GB4T8DA8N/' +
  'BgaG/wwMDP8ZGBj+MzAw/GdgYPjPwMDwn4GB4T8DA8N/BgaG/wwMDAysDAwMowAAkOQT/2pCwIYAAAAASUVORK5CYII=';

const POINTS: GeoJSON.FeatureCollection = {
  type: 'FeatureCollection',
  features: [
    { type: 'Feature', geometry: { type: 'Point', coordinates: [13.405, 52.52] }, properties: { name: 'Mitte' } },
    { type: 'Feature', geometry: { type: 'Point', coordinates: [13.45, 52.5] }, properties: { name: 'Friedrichshain' } },
    { type: 'Feature', geometry: { type: 'Point', coordinates: [13.36, 52.51] }, properties: { name: 'Tiergarten' } },
  ],
};

// Lives inside <LazyMapContainer> so it has the MapProvider context that
// `useMapImages` reads. Registers the icon image, then renders a symbol layer.
function IconLayer() {
  const { ready } = useMapImages([{ id: 'pin', url: PIN_ICON }]);
  if (!ready) return null;
  return (
    <MapSource id="places" data={POINTS}>
      <MapLayer
        {...createSymbolLayer({
          id: 'places-icons',
          sourceId: 'places',
          iconImage: 'pin',
          iconSize: 1.5,
          textField: ['get', 'name'],
        })}
      />
    </MapSource>
  );
}

/**
 * Custom icons (data-driven symbol layer) — register an icon image with
 * `useMapImages`, then draw one icon per GeoJSON feature via
 * `createSymbolLayer`. This is the scalable path for many markers; for a
 * handful of rich markers, use `MapMarker` with `children`/`color`/`size`.
 */
export const CustomIcons: Story = {
  name: 'Custom icons (symbol layer)',
  render: () => (
    <Frame>
      <LazyMapContainer
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
      >
        <IconLayer />
      </LazyMapContainer>
    </Frame>
  ),
};

/**
 * Measure — click on the map to measure a path's length (distance mode) or a
 * polygon's area (area mode). Toggle the ruler to start measuring, switch
 * modes, read the live total, and clear. Renders through the existing
 * line / polygon layer factories.
 */
export const Measure: Story = {
  render: () => (
    <Frame>
      <LazyMapContainer
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
        scrollProtection={false}
      >
        <MeasureControl />
      </LazyMapContainer>
    </Frame>
  ),
};

/**
 * Basemaps — switch among the built-in styles. CARTO (`light`/`dark`/
 * `streets`) and **OpenFreeMap** (`liberty`/`bright`/`positron`) are
 * key-free; `satellite` (MapTiler) needs an API key and is omitted here.
 * OpenFreeMap is a genuinely-free public instance (no key, no limits).
 */
export const Basemaps: Story = {
  render: function BasemapsStory() {
    const keys = (Object.keys(MAP_STYLES) as MapStyleKey[]).filter((k) => k !== 'satellite');
    const [style, setStyle] = useState<MapStyleKey>('liberty');
    return (
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap gap-1.5">
          {keys.map((k) => (
            <button
              key={k}
              type="button"
              onClick={() => setStyle(k)}
              className={
                'rounded-md border px-2.5 py-1 text-xs font-medium transition-colors ' +
                (style === k
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-border bg-card text-foreground hover:bg-accent')
              }
            >
              {k}
            </button>
          ))}
        </div>
        <Frame>
          <LazyMapContainer
            key={style}
            mapStyle={style}
            initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
          >
            <MapMarker marker={BERLIN} ariaLabel="Berlin DC" />
          </LazyMapContainer>
        </Frame>
      </div>
    );
  },
};

/**
 * 3D terrain — `terrain` renders elevation + hillshade from the free AWS
 * Terrarium DEM (no API key) and eases the camera pitch in so it reads as
 * 3D. Toggle it at runtime with the Mountain chip in the top-right toolbar.
 * Shown over the Swiss Alps where the relief is dramatic.
 */
export const Terrain3D: Story = {
  name: '3D terrain + hillshade',
  render: () => (
    <Frame>
      <LazyMapContainer
        mapStyle="streets"
        terrain
        initialViewport={{ longitude: 7.96, latitude: 46.02, zoom: 11, pitch: 60 }}
      />
    </Frame>
  ),
};

/**
 * Compass — the Google-style reset-to-north chip. Loaded already rotated
 * (`bearing: 40`) and tilted (`pitch: 50`), so the compass appears in the
 * top-right toolbar from the start. Its needle counter-rotates to keep
 * pointing at true north, and it reads as an **accent color** (`text-primary`)
 * to signal you're off true north. Click it: the camera eases back to a
 * north-up, top-down view, the bearing/pitch hit zero, and the chip
 * disappears (a flat north-up map needs no compass). Rotate/tilt again with
 * right-drag, Ctrl+drag, or two fingers to bring it back.
 */
export const Compass: Story = {
  name: 'Compass (reset to north)',
  render: () => (
    <Frame>
      <LazyMapContainer
        mapStyle="streets"
        initialViewport={{
          longitude: BERLIN.longitude,
          latitude: BERLIN.latitude,
          zoom: 11,
          bearing: 40,
          pitch: 50,
        }}
      >
        <MapMarker marker={BERLIN} ariaLabel="Berlin DC" />
      </LazyMapContainer>
    </Frame>
  ),
};

/**
 * Geolocate — the Google-style "locate me" chip. `geolocate` adds a
 * `LocateFixed` chip to the top-right toolbar that drives maplibre's built-in
 * `GeolocateControl`: pressing it centers + follows you (track mode) and draws
 * a location dot + accuracy circle. The chip tints `text-primary` while
 * following and shows a muted/disabled look (with an explanatory tooltip) if
 * permission is denied or location is unavailable.
 *
 * Privacy: **off by default** — nothing prompts for location until you set
 * `geolocate` AND press the chip. Requires a **secure context** (HTTPS /
 * localhost); in Storybook you must click the chip and allow the browser
 * prompt. Works inside the fullscreen dialog too.
 */
export const Geolocate: Story = {
  name: 'Geolocate (locate-me chip)',
  render: () => (
    <Frame>
      <LazyMapContainer
        geolocate
        geolocateOptions={{ highAccuracy: true }}
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
        onGeolocate={(pos) => console.log('geolocate fix', pos)}
        onGeolocateError={(err) => console.warn('geolocate error', err.message)}
      >
        <MapMarker marker={BERLIN} ariaLabel="Berlin DC" />
      </LazyMapContainer>
    </Frame>
  ),
};

/**
 * `useGeolocation` — the raw browser-position hook (no map dependency).
 * Nothing happens until you press a button (it then prompts the OS for
 * permission). Needs a secure context (HTTPS/localhost). Use this for
 * custom UI; for the on-map dot + follow, use `MapContainer`'s `geolocate`.
 */
export const UseGeolocationHook: Story = {
  name: 'useGeolocation (hook)',
  render: function GeolocationDemo() {
    const geo = useGeolocation({ highAccuracy: true });
    return (
      <div className="flex w-[420px] flex-col gap-3 rounded-xl border border-border bg-card p-4 text-sm">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={geo.request}
            className="rounded-md border border-border bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:opacity-90"
          >
            Locate me
          </button>
          <button
            type="button"
            onClick={geo.watch}
            className="rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent"
          >
            Watch
          </button>
          <button
            type="button"
            onClick={geo.stop}
            className="rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent"
          >
            Stop
          </button>
        </div>
        <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 font-mono text-xs text-muted-foreground">
          <dt>status</dt>
          <dd className="text-foreground">{geo.status}</dd>
          <dt>supported</dt>
          <dd className="text-foreground">{String(geo.supported)}</dd>
          <dt>lat, lng</dt>
          <dd className="text-foreground">
            {geo.position ? `${geo.position.lat.toFixed(5)}, ${geo.position.lng.toFixed(5)}` : '—'}
          </dd>
          <dt>accuracy</dt>
          <dd className="text-foreground">
            {geo.position ? `${Math.round(geo.position.accuracy)} m` : '—'}
          </dd>
          <dt>heading</dt>
          <dd className="text-foreground">{geo.position?.heading ?? '—'}</dd>
          <dt>error</dt>
          <dd className="text-foreground">{geo.error?.message ?? '—'}</dd>
        </dl>
      </div>
    );
  },
};

/**
 * Geocoder (input only) — a standalone, map-free address/place autocomplete.
 * Type ≥3 chars; results stream in from the injectable resolver (default =
 * the free, key-free public **Photon** endpoint). Pick one and the chosen
 * `GeocodeResult` shows below.
 *
 * NOTE: hits public Photon (`photon.komoot.io`) directly — needs network,
 * is fair-use, and uses **no API key**. For production, pass your own
 * `resolve` (a Wails/Go method or a Next.js API route proxying Photon / a
 * self-hosted instance) to dodge CORS + throttling.
 */
export const Geocoder: Story = {
  name: 'Geocoder (input)',
  render: function GeocoderDemo() {
    const [picked, setPicked] = useState<GeocodeResult | null>(null);
    return (
      <div className="w-[420px] space-y-3">
        <GeocoderInput onSelect={setPicked} placeholder="Search a place…" />
        <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 rounded-lg border border-border bg-card p-3 font-mono text-xs text-muted-foreground">
          <dt>label</dt>
          <dd className="text-foreground">{picked?.label ?? '—'}</dd>
          <dt>secondary</dt>
          <dd className="text-foreground">{picked?.secondary ?? '—'}</dd>
          <dt>lng, lat</dt>
          <dd className="text-foreground">
            {picked ? `${picked.lng.toFixed(5)}, ${picked.lat.toFixed(5)}` : '—'}
          </dd>
        </dl>
      </div>
    );
  },
};

/**
 * Geocoder on the map — set `geocoder` on `LazyMapContainer` and a
 * Google-Maps-style magnifier chip appears in the toolbar. Click it to reveal
 * an autofocused search box (top-left); pick a result and the camera flies
 * there (zoom ~14), drops a pin, and the box closes. Esc / re-clicking the
 * chip also closes it. Search is biased to the current map center. Hits public
 * Photon (network, fair-use, no key) — pass `geocoderResolve` in production.
 */
export const GeocoderOnMap: Story = {
  name: 'Geocoder (on map)',
  render: () => (
    <Frame>
      <LazyMapContainer
        geocoder
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
      />
    </Frame>
  ),
};

/**
 * Geocoder (always-on) — the standalone `GeocoderControl` rendered as a child,
 * an always-visible top-left search box (no toolbar toggle). This is the
 * backward-compatible path for hosts that want the box permanently shown;
 * prefer the `geocoder` toolbar chip (see "Geocoder (on map)") for the
 * Google-Maps-style collapsed UX.
 */
export const GeocoderAlwaysOn: Story = {
  name: 'Geocoder (always-on)',
  render: () => (
    <Frame>
      <LazyMapContainer
        initialViewport={{ longitude: BERLIN.longitude, latitude: BERLIN.latitude, zoom: 11 }}
      >
        <GeocoderControl />
      </LazyMapContainer>
    </Frame>
  ),
};

/**
 * Draggable markers — a controlled `positions` / `onChange` layer over the
 * native `MapMarker` drag. Drag a pin: its `{ lng, lat }` commits on drop and
 * the readout below updates from React state.
 */
function DraggableMarkersHost() {
  const [positions, setPositions] = useState<DraggablePoint[]>([
    { id: 'a', lng: 13.405, lat: 52.52, label: 'Brandenburg Gate' },
    { id: 'b', lng: 13.428, lat: 52.5, label: 'East Side Gallery' },
  ]);

  return (
    <div className="w-[560px] space-y-3">
      <Frame>
        <LazyMapContainer
          initialViewport={{ longitude: 13.41, latitude: 52.51, zoom: 12 }}
        >
          <DraggableMarkers positions={positions} onChange={setPositions} />
        </LazyMapContainer>
      </Frame>
      <p className="text-sm text-muted-foreground">
        Drag a pin to move it — the coordinates below update on drop.
      </p>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 font-mono text-xs text-muted-foreground">
        {positions.map((p) => (
          <div key={p.id} className="contents">
            <dt>{p.label ?? p.id}</dt>
            <dd className="text-foreground">
              {p.lng.toFixed(5)}, {p.lat.toFixed(5)}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export const DraggableMarkersStory: Story = {
  name: 'Draggable markers',
  render: () => <DraggableMarkersHost />,
};

// ============================================================================
// Marker info-cards — Google-Maps-style card popup above a pin
// ============================================================================

const CARD_MARKERS: MarkerWithCard[] = [
  {
    id: 'brandenburg',
    longitude: 13.3777,
    latitude: 52.5163,
    card: {
      title: 'Brandenburg Gate',
      badge: 'Landmark',
      description:
        '18th-century neoclassical monument and one of Berlin’s best-known landmarks, built on the orders of Frederick William II.',
      image:
        'https://images.unsplash.com/photo-1560969184-10fe8719e047?auto=format&fit=crop&w=400&q=60',
      actions: [
        { label: 'Directions', href: 'https://maps.google.com', variant: 'default' },
        { label: 'Website', href: 'https://www.berlin.de', variant: 'outline' },
      ],
    },
  },
  {
    id: 'museum-island',
    longitude: 13.3971,
    latitude: 52.5169,
    card: {
      title: 'Museum Island',
      badge: 'UNESCO',
      description:
        'A complex of five internationally significant museums on the northern half of the Spree Island in central Berlin.',
    },
  },
  {
    id: 'tv-tower',
    longitude: 13.4094,
    latitude: 52.5208,
    // No `card` — this one uses the custom `renderCard` below.
  },
];

/**
 * `MapMarkers` is the "just works" marker layer. Click a pin → a card opens
 * ABOVE it (anchor `bottom`); click another → the first closes (one card at a
 * time). Two markers carry default `card` data; the TV-tower marker uses a
 * custom `renderCard`. Outside-click / Esc / the close button dismiss.
 */
export const MarkerCards: Story = {
  name: 'Marker info-cards',
  render: () => (
    <Frame>
      <LazyMapContainer
        initialViewport={{ longitude: 13.395, latitude: 52.518, zoom: 13 }}
      >
        <MapMarkers
          markers={CARD_MARKERS}
          renderCard={(marker, close) =>
            // The seam: `renderCard` (when set) owns ALL open markers. Here we
            // fall back to the default `MarkerCard` for data-bearing markers
            // and supply fully-custom content for the TV-tower marker.
            marker.card ? (
              <MarkerCard {...marker.card} />
            ) : (
              <div className="max-w-[240px] rounded-lg border border-border bg-popover p-3 text-popover-foreground shadow-md">
                <p className="text-sm font-medium text-foreground">Berlin TV Tower</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Custom <code>renderCard</code> content — full control over the
                  popup body.
                </p>
                <button
                  type="button"
                  onClick={close}
                  className="mt-2 text-xs font-medium text-primary underline-offset-4 hover:underline"
                >
                  Close
                </button>
              </div>
            )
          }
        />
      </LazyMapContainer>
    </Frame>
  ),
};
