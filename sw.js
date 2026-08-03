const CACHE_NAME = 'ocean-uni-map-v96';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './css/style.css?v=96.0.0',
  './css/leaflet.css?v=55.0.0',
  './js/leaflet.js?v=96.0.0',
  './js/campus_data_fallback.js?v=96.0.0',
  './js/i18n.js?v=96.0.0',
  './js/routing.js?v=96.0.0',
  './js/cms.js?v=96.0.0',
  './js/app.js?v=96.0.0',
  './data/Drawing.geojson',
  './data/campus_data.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[PWA SW] Pre-caching core campus navigation assets...');
      return cache.addAll(ASSETS_TO_CACHE).catch(err => console.log('[PWA SW] Pre-cache warning:', err));
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[PWA SW] Clearing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse));
          }
        }).catch(() => {});
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
