// Script to receive theme from parent
        (function () {
            'use strict';

            // Listen for messages from parent
            window.addEventListener('message', function (event) {
                // Verify origin (replace with your parent page origin)
                if (event.origin !== '{{ COURSES_BASE_URL }}') return;

                // Check if it's a theme message
                if (event.data && event.data.type === 'theme') {
                    applyTheme(event.data.mode);
                }
            }, false);

            // Function to apply the theme
            function applyTheme(mode) {
                // Remove existing theme classes
                document.body.classList.remove('theme-dark', 'theme-light');

                // Add the appropriate theme class
                document.body.classList.add('theme-' + mode);

                // Store theme preference
                localStorage.setItem('theme', mode);

                // Optional: Notify parent that theme was applied
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'theme-applied',
                        mode: mode
                    }, '{{ COURSES_BASE_URL }}');
                }
            }

        })();