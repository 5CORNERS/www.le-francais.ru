var CACHE_NAME = 'le_francais-conjugation-cache-v1';
var urlsToCache = [
    '/conjugaison/',
    '/static/conjugation/css/conjugation.min.css',
    '/static/conjugation/js/conjugation.min.js',
    '/static/conjugation/images/ui-anim_basic_16x16.gif',
    '/static/lib/jquery-ui-1.12.1.custom/jquery-ui.min.css',
];
self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request)
            .then(function (response) {
                if (response) {
                    return response;
                }
                return fetch(event.request).then(
                    function (response) {
                        if (!response ||
                            response.status !== 200 ||
                            response.type !== 'basic' ||
                            event.request.method !== 'GET' ||
                            !event.request.url.includes('/conjugation/') &&
                            !event.request.url.includes('/conjugaison/')
                        ) {
                            return response;
                        }
                        var responseToCache = response.clone();
                        caches.open(CACHE_NAME)
                            .then(function (cache) {
                                cache.put(event.request, responseToCache);
                            });
                        return response;
                    }
                );
            })
    );
});
