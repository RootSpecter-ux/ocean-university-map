const CACHE_NAME = 'ocean-uni-map-v101';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[PWA SW] Deleting stale cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Network-First Strategy to ensure users always get the latest campus drawings & code
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    fetch(event.request).then((networkResponse) => {
      if (networkResponse && networkResponse.status === 200) {
        const responseClone = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
      }
      return networkResponse;
    }).catch(() => {
      return caches.match(event.request);
    })
  );
});
