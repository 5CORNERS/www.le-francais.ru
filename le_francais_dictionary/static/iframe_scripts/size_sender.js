$(
    function () {
        // Track the last sent height to prevent feedback loops
        let lastSentHeight = 0;

        // Function to calculate and send the height
        function sendHeight() {
            // Get the height of the document
            const height = Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            );

            // Only send message if height actually changed by more than 5px
            // This prevents minor fluctuations from causing messages
            if (Math.abs(height - lastSentHeight) > 5) {
                lastSentHeight = height;

                // Send the height to the parent
                window.parent.postMessage({
                    type: 'resize',
                    height: height
                }, COURSES_BASE_URL || "*");

                console.log('Sent height: ' + height); // For debugging
            }

        }

        // Send height on load (after a slight delay to ensure content is rendered)
        setTimeout(sendHeight, 100);


        // Throttle function to limit resize calculations
        function throttle(func, limit) {
            let inThrottle;
            return function () {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }

        // Use throttled version for resize events
        window.addEventListener('resize', throttle(sendHeight, 100));

        // Improved MutationObserver to avoid feedback loops
        const observer = new MutationObserver(throttle(function (mutations) {
            // Filter mutations to ignore style attribute changes on body
            // which might be caused by the parent setting the height
            const relevantMutations = mutations.filter(mutation => {
                // Ignore style attribute changes on body element
                return !(mutation.type === 'attributes' &&
                    mutation.attributeName === 'style' &&
                    mutation.target === document.body);
            });

            if (relevantMutations.length > 0) {
                sendHeight();
            }
        }, 100));

        // Start observing with more targeted settings
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'id', 'src'], // Ignore style changes
            characterData: true
        });
    }
);