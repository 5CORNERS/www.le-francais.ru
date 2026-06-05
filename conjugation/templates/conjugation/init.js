{% load static %}
(function() {
    // 1. Динамическая загрузка JavaScript модуля
    const scripts = [
        '{% static "conjugation/js/dictionary.min.js" %}'
    ];
    scripts.forEach(function (src) {
        if (!document.querySelector(`script[src="${src}"]`)) {
            let script = document.createElement("script");
            script.setAttribute("src", src);
            script.setAttribute("type", "text/javascript");
            script.setAttribute("async", "true");
            document.getElementsByTagName("head")[0].appendChild(script);
        }
    });

    // 2. Динамическая загрузка CSS стилей модуля
    const stylesheets = [
        '{% static "conjugation/css/dictionary.min.css" %}'
    ];
    stylesheets.forEach(function (href) {
        if (!document.querySelector(`link[href="${href}"]`)) {
            let link = document.createElement("link");
            link.setAttribute("href", href);
            link.setAttribute("rel", "stylesheet");
            link.setAttribute("type", "text/css");
            document.getElementsByTagName("head")[0].appendChild(link);
        }
    });
})();