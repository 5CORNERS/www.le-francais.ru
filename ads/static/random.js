let observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const div = entry.target
            pushAdToQueue(div)
            observer.unobserve(div)
        }
    })
}, {threshold: [0], rootMargin: '600px 0px 600px 0px'})

function getSizes(data, containerWidth, viewPortWidth, containerHeight = Number.MAX_VALUE, viewPortHeight = Number.MAX_VALUE) {
    const mapping = data.find(m => (
        m[0][0] === 'v' && m[0][1][0] <= viewPortWidth && m[0][1][1] <= viewPortHeight
    ) || (m[0][0] === 'c' && m[0][1][0] <= containerWidth && m[0][1][1] <= containerHeight))
    return mapping[1]
}

function includeAd(id) {
    let $div = $(document.getElementById(id));
    observer.observe($div.get(0))
}

let queuedLoads = [];
let timerId;

function pushAdToQueue(div) {
    queuedLoads.push(div);
    if (timerId){
        return
    }
    timerId = setInterval(() => {
        if (!queuedLoads.length) {
            clearInterval(timerId);
            timerId = null;
            return
        }
        let nextDiv = queuedLoads.shift();
        loadAd(nextDiv)
    }, 1000)
}

function loadAd(div) {
    let $div = $(div);
    let id = $div.attr('id')
    if (typeof window.pageViewID === 'undefined') {
        window.pageViewID = id;
    }
    let containerWidth = $div.parent().width();
    $div.data('container-width', containerWidth)
    let sizes = $div.data('sizes');
    let allowableSizes
    if (Array.isArray(sizes) && sizes.length) {
        allowableSizes = getSizes(sizes, containerWidth, window.innerWidth)
    }else{
        allowableSizes = []
    }

    $div.data('sizes', allowableSizes).data('container-width', containerWidth)
    $.ajax(Urls['ads:getCreative'](), {
        method: 'GET',
        data: {
            sizes: allowableSizes.map((size, i) => {
                return `${size[0]}x${size[1]}:${size[2]}`
            }),
            ad_unit_name: $div.data('unit-name'),
            placement: $div.data('unit-placement'),
            ad_unit_utm_source: $div.data('unit-utm-source'),
            page_view_id: window.pageViewID,
            max_width: $div.data('container-width')
        },
        traditional: true,
        dataType: 'json',
        statusCode: {
            200: (data) => {
                if (data['head_html']) {
                    $('head').append(data['head_html'])
                }
                $div.append(data['body_html']);
            },
            404: () => {

            }
        }
    })
}
