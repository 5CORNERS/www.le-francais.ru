var CACHE_NAME = 'le_francais-conjugation-cache-v1';
var urlsToCache = [
    '/static/conjugation/css/conjugation.min.css',
    '/static/conjugation/js/conjugation.min.js',
    '/static/conjugation/images/ui-anim_basic_16x16.gif',
    '/static/lib/jquery-ui-1.12.1.custom/jquery-ui.min.css',
    '/static/js/le_francais.min.js',
    '/static/css/le_francais.min.css',
    '/android-chrome-192x192.png',
    '/android-chrome-512x512.png',
    '/static/components/css/bootstrap.css',
    '/static/components/css/bootstrap-select.css',
    '/static/components/css/bootstrap-treeview.css',
    '/static/components/css/font-awesome.css',
    '/static/components/js/bootstrap.js',
    '/static/components/js/bootstrap-select.js',
    '/static/components/js/bootstrap-treeview.min.js',
    '/static/components/js/jquery.js',
];

self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.delete(CACHE_NAME).then(function () {
            caches.open(CACHE_NAME).then(function (cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
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
                            event.request.url.includes('/api/') ||
                            !event.request.url.includes('/static/')
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
