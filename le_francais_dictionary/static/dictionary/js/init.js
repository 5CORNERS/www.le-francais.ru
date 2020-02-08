(function() {
	['app.7cccc1b4.js', 'chunk-vendors.61a3befe.js'].forEach(function (src) {
		let script = document.createElement("script");
		script.setAttribute("src", `/static/dictionary/js/${src}`);
		script.setAttribute("type", "text/javascript");
		script.setAttribute("async", "true");
		document.getElementsByTagName("head")[0].appendChild(script);
	});

	['app.ed26fe1e.css', 'chunk-vendors.c7c67c91.css'].forEach(function (href) {
		let script = document.createElement("link");
		script.setAttribute("href", `/static/dictionary/css/${href}`);
		script.setAttribute("rel", "stylesheet");
		script.setAttribute("type", "text/css");
		document.getElementsByTagName("head")[0].appendChild(script);
	});
})();
