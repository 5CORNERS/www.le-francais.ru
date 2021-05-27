function getNavRootId() {
    return $('meta[name="nav-root-id"]').attr("content")
}

function resizeIframe(obj) {
    obj.style.height = obj.contentWindow.document.body.scrollHeight + 'px';
}

function getPageId() {
    return $('meta[name="page-id"]').attr("content")
}

function voice(src){
    let audio = new Audio(src);
    audio.play();
}

function bind_play_icons() {
    let play_icons = $('.play[data-audiosrc]');
    play_icons.unbind();
    play_icons.click(event => {
        let url = $(event.target).data('audiosrc');
        voice(url)
    });
    play_icons.keypress(e => {
        if (e.charCode === 13 || e.charCode === 32){
            e.preventDefault()
            let url = $(e.target).data('audiosrc');
            voice(url)
        }
    })
}

window.setIntervalRun = function (interval, callbackFunction, args) {
    let internal = {
        interval: interval,
        stopTime: undefined,
        callback: function () {
            callbackFunction(args)
        },
        stopped: false,
        runLoop: function () {
            if (internal.stopped) return;
            internal.callback.call(this);
            internal.loop()
        },
        stop: function () {
            if (!this.stopped) {
                this.stopped = true;
                window.clearTimeout(this.timeout);
                this.stopTime = Date.now();
            }
        },
        start: function (firstRun = undefined) {
            this.stopped = false;
            if (Date.now() - this.stopTime > this.interval) {
                this.callback.call(this)
            } else if (firstRun) {
                this.callback.call(this)
            }
            return this.loop();
        },
        loop: function () {
            this.timeout = window.setTimeout(this.runLoop, this.interval);
            return this;
        }
    };
    return internal.start(true)
};

function setNodeState(href, isExpanded) {
    var nodesCollapsedState = localStorage.getItem("nodesCollapsedState") != null ?
        JSON.parse(localStorage.getItem("nodesCollapsedState")) :
        {};
    nodesCollapsedState[href] = isExpanded;
    localStorage.setItem("nodesCollapsedState", JSON.stringify(nodesCollapsedState))
}

function showModal(url, data) {
    $.ajax({
        url: url,
        type: 'GET',
        data: data,
        datatype: 'html',
        success: function (body) {
            let modal = $(body);
            modal.modal('show');
        }
    })
}

function addExpandedStateToNavdata(navData) {
    var state = localStorage.getItem("nodesCollapsedState") != null ?
        JSON.parse(localStorage.getItem("nodesCollapsedState")) :
        {};
    navData.forEach(function (node) {
        var href = navData.href;
        if (href in state) {
            var expanded = state[href];

            node.state.expanded = expanded
        }
        if (node.nodes) {
            addExpandedStateToNavdata(node.nodes);
            node.nodes.forEach(function (child) {
                if (child.state && (child.state.expanded || child.state.selected)) {
                    node.state.expanded = true;
                }
            })
        }
        if (node.state && node.state.selected) {
            node.state.expanded = true;
        }
    });
    return navData
}

function scrolling(document, history, location) {
    const HISTORY_SUPPORT = !!(history && history.pushState);

    const anchorScrolls = {
        ANCHOR_REGEX: /^#[^ ]+$/,
        OFFSET_HEIGHT_PX: 71,

        /**
         * Establish events, and fix initial scroll position if a hash is provided.
         */
        init: function () {
            this.scrollToCurrent();
            $(window).on('hashchange', $.proxy(this, 'scrollToCurrent'));
            $('body').on('click', 'a', $.proxy(this, 'delegateAnchors'));
        },

        /**
         * Return the offset amount to deduct from the normal scroll position.
         * Modify as appropriate to allow for dynamic calculations
         */
        getFixedOffset: function () {
            return this.OFFSET_HEIGHT_PX;
        },

        /**
         * If the provided href is an anchor which resolves to an element on the
         * page, scroll to it.
         * @param  {String} href
         * @return {Boolean} - Was the href an anchor.
         */
        scrollIfAnchor: function (href, pushToHistory) {
            var match, anchorOffset;

            if (!this.ANCHOR_REGEX.test(href)) {
                return false;
            }

            match = document.getElementsByName(href.slice(1));

            if (match) {
                anchorOffset = $(match).offset().top - this.getFixedOffset();
                $('html, body').animate({scrollTop: anchorOffset});

                // Add the state to history as-per normal anchor links
                if (HISTORY_SUPPORT && pushToHistory) {
                    history.pushState({}, document.title, location.pathname + href);
                }
            }

            return !!match;
        },

        /**
         * Attempt to scroll to the current location's hash.
         */
        scrollToCurrent: function (e) {
            if (this.scrollIfAnchor(window.location.hash) && e) {
                e.preventDefault();
            }
        },

        /**
         * If the click event's target was an anchor, fix the scroll position.
         */
        delegateAnchors: function (e) {
            var elem = e.target;

            if (this.scrollIfAnchor(elem.getAttribute('href'), true)) {
                e.preventDefault();
            }
        }
    };

    $.proxy(anchorScrolls, 'init');
}

$(document).ready(function () {
    $(function () {
        let timerId
        $(window).resize(function () {
            clearTimeout(timerId);
            let resizeHandler =function () {
                $('div.lazy-image-container>img').each(() => {
                    let $img = $(this)
                    let $div = $img.parent()
                    let aspect = $div.data('aspect')
                    $div.css('height', aspect * $div.width())
                })
                console.log('resize complete')
            }
            if (!timerId){
                resizeHandler()
            }else{timerId = setTimeout(resizeHandler, 300);}

        }).resize();
    })

    var navTreeElement = document.getElementById("sidebar");
    if (navTreeElement != null) {
        $.getJSON('/api/nav/?rootId=' + getNavRootId() + '&pageId=' + getPageId(), function (navData) {
            navData = addExpandedStateToNavdata(navData);
            $(navTreeElement).treeview({
                levels: 0,
                data: navData,
                onNodeSelected: function (event, data) {
                    window.location.href = data.href;
                },
                onNodeExpanded: function (event, data) {
                    setNodeState(data.href, true)
                },
                onNodeCollapsed: function (event, data) {
                    setNodeState(data.href, false)
                }
            });
        });
        $(".sidebar-collapse-button").click(function () {
            var $target = $($(this).data("target"));
            $target.toggleClass('active');
            $(this).attr('aria-expanded', $target.hasClass('active'));
        });
    }

    // Disable backdrop modal if Safari
    $(document).on('show.bs.modal', '.modal', function () {
      $(this).data('bs.modal')._config.backdrop = 'static';
    });


    // Javascript to enable link to tab
    var hash = document.location.hash;
    if (hash != "") {
        hash = hash.substring(1);
        $('.nav-tabs a[href="#' + hash + '"]').tab('show');
    }/* else {
        $('.nav-tabs a:first').tab('show');
    }*/

    window.onhashchange = function () {
        $('.nav-tabs a[href="#' + location.hash.substring(1) + '"]').tab('show');
    };

    // Change hash for page-reload
    $('.nav-tabs a').on('shown.bs.tab', function (e) {
        history.pushState(null, null, e.target.hash);
    });

    // Toggle tooltips
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
    bind_play_icons()

    // Scrolling

	scrolling(window.document, window.history, window.location);

});

(function () {
    'use strict';
    /**
     * Converts details/summary tags into working elements in browsers that don't yet support them.
     * @return {void}
     */
    var details = (function () {

        var isDetailsSupported = function () {
            // https://mathiasbynens.be/notes/html5-details-jquery#comment-35
            // Detect if details is supported in the browser
            var el = document.createElement("details");
            var fake = false;

            if (!("open" in el)) {
                return false;
            }

            var root = document.body || function () {
                var de = document.documentElement;
                fake = true;
                return de.insertBefore(document.createElement("body"), de.firstElementChild || de.firstChild);
            }();

            el.innerHTML = "<summary>a</summary>b";
            el.style.display = "block";
            root.appendChild(el);
            var diff = el.offsetHeight;
            el.open = true;
            diff = diff !== el.offsetHeight;
            root.removeChild(el);

            if (fake) {
                root.parentNode.removeChild(root);
            }

            return diff;
        }();

        if (!isDetailsSupported) {
            var blocks = document.querySelectorAll("details>summary");
            for (var i = 0; i < blocks.length; i++) {
                var summary = blocks[i];
                var details = summary.parentNode;

                // Apply "no-details" to for unsupported details tags
                if (!details.className.match(new RegExp("(\\s|^)no-details(\\s|$)"))) {
                    details.className += " no-details";
                }

                summary.addEventListener("click", function (e) {
                    var node = e.target.parentNode;
                    if (node.hasAttribute("open")) {
                        node.removeAttribute("open");
                    } else {
                        node.setAttribute("open", "open");
                    }
                });
            }
        }
    });

    (function () {
        var onReady = function onReady(fn) {
            if (document.addEventListener) {
                document.addEventListener("DOMContentLoaded", fn);
            } else {
                document.attachEvent("onreadystatechange", function () {
                    if (document.readyState === "interactive") {
                        fn();
                    }
                });
            }
        };

        onReady(function () {
            details();
        });
    })();

}());

function forceLower(strInput) {
    strInput.value = strInput.value.toLowerCase();
}

$(function () {
  $('[data-toggle="popover"]').popover({
      boundary: 'viewport'
  })
});

$('video').each(function () {this.controls = true});
