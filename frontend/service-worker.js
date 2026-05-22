const CACHE_NAME = 'parsia-waiter-v1';
const ASSETS = [
  './waiter.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
];

// Install: cache static assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

// Activate: remove old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network first for API, cache first for assets
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API calls always go to network
  if (url.hostname === 'parsia-restaurant.onrender.com') {
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(JSON.stringify({ error: 'Offline' }), {
          headers: { 'Content-Type': 'application/json' }
        })
      )
    );
    return;
  }

  // Static assets: cache first, fallback to network
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
