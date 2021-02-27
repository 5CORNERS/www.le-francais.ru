(function() {
	['%APP_JS%', '%APP_BUNDLE_JS%'].forEach(function (src) {
		let script = document.createElement("script");
		script.setAttribute("src", `/static/dictionary/js/${src}`);
		script.setAttribute("type", "text/javascript");
		script.setAttribute("async", "true");
		document.getElementsByTagName("head")[0].appendChild(script);
	});

	['%APP_CSS%', '%APP_BUNDLE_CSS%'].forEach(function (href) {
		let script = document.createElement("link");
		script.setAttribute("href", `/static/dictionary/css/${href}`);
		script.setAttribute("rel", "stylesheet");
		script.setAttribute("type", "text/css");
		document.getElementsByTagName("head")[0].appendChild(script);
	});
})();
