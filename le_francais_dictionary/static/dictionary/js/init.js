(function() {
	['app.b6f37687.js', 'chunk-vendors.e3473f2e.js'].forEach(function (src) {
		let script = document.createElement("script");
		script.setAttribute("src", `/static/dictionary/js/${src}`);
		script.setAttribute("type", "text/javascript");
		script.setAttribute("async", "true");
		document.getElementsByTagName("head")[0].appendChild(script);
	});

	['app.a8aca2ee.css', 'chunk-vendors.7bcf2756.css'].forEach(function (href) {
		let script = document.createElement("link");
		script.setAttribute("href", `/static/dictionary/css/${href}`);
		script.setAttribute("rel", "stylesheet");
		script.setAttribute("type", "text/css");
		document.getElementsByTagName("head")[0].appendChild(script);
	});
})();
