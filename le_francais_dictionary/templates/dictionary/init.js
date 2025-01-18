{% load static %}(function() {
	['{% static "dictionary/js/app.js" %}', '{% static "dictionary/js/chunk-vendors.js" %}'].forEach(function (src) {
		let script = document.createElement("script");
		script.setAttribute("src", `${src}`);
		script.setAttribute("type", "text/javascript");
		script.setAttribute("async", "true");
		document.getElementsByTagName("head")[0].appendChild(script);
	});

	['{% static "dictionary/css/app.css" %}', '{% static "dictionary/css/chunk-vendors.css" %}'].forEach(function (href) {
		let script = document.createElement("link");
		script.setAttribute("href", `${href}`);
		script.setAttribute("rel", "stylesheet");
		script.setAttribute("type", "text/css");
		document.getElementsByTagName("head")[0].appendChild(script);
	});
})();
