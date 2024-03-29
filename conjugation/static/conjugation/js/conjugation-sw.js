const CACHE_NAME = 'le_francais-conjugation-cache-v31';
const urlsMatchToCache = [
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
    '/static/components/js/jquery.js'
];
const urlsInToCache = [
    '/static/',
    '/verbs_autocomplete/',
    '/polly/',
]
const urlsInFromNetwork = [

]

self.addEventListener('activate', event => {
    let cacheKeepList = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(keyList => {
            return Promise.all(keyList.map(key => {
                if (cacheKeepList.indexOf(key) === -1) {
                    return caches.delete(key);
                }
            }))
        })
    )
});

const putInCache = async (request, response) => {
  const cache = await caches.open(CACHE_NAME);
  await cache.put(request, response);
};

const fetchRequest = async ({ request }) => {
    const responseFromCache = await caches.match(request);
    if (responseFromCache) {
        return responseFromCache
    }
    try {
        const responseFromNetwork = await fetch(request);
        if (urlsInToCache.some(u => request.url.includes(u)) || urlsMatchToCache.some(u => request.url === u)) {
            putInCache(request, responseFromNetwork.clone())
        }
        return responseFromNetwork
    } catch (error) {
        return new Response("Network Error", {
            status:408,
            headers: {"Content-Type": "text/plain"}
        })
    }
}

self.addEventListener('fetch', function (event) {
    event.respondWith(
        fetchRequest({
            request: event.request
        })
    )
});
