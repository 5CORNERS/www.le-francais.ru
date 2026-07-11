(function () {
    'use strict';
    window.addEventListener('message', function (event) {
        if (event.origin !== '{{ COURSES_BASE_URL }}') return;
        if (event.data && event.data.type === 'theme') {
            applyTheme(event.data.mode);
        }
    }, false);
    function applyTheme(mode) {
        document.body.classList.remove('theme-dark', 'theme-light');
        document.body.classList.add('theme-' + mode);
        localStorage.setItem('theme', mode);
        if (window.parent !== window) {
            window.parent.postMessage({
                type: 'theme-applied',
                mode: mode
            }, '{{ COURSES_BASE_URL }}');
        }
    }
})();