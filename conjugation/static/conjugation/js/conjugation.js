// if ('serviceWorker' in navigator) {
//   window.addEventListener('load', function() {
//     navigator.serviceWorker.register('/static/conjugation/js/conjugation-sw.js', {
//       'scope': '/conjugaison/'
//     }).then(function(registration) {
//       // Registration was successful
//       console.log('ServiceWorker registration successful with scope: ', registration.scope);
//     }, function(err) {
//       // registration failed :(
//       console.log('ServiceWorker registration failed: ', err);
//     });
//   });
// }

let deferredPrompt;

var isTooSoon = true;
window.addEventListener("beforeinstallprompt", function(e) {
  deferredPrompt = e;
  if (isTooSoon) {
    deferredPrompt.preventDefault(); // Prevents prompt display
    // Prompt later instead:
    setTimeout(function() {
      isTooSoon = false;
      deferredPrompt.prompt(); // Throws if called more than once or default not prevented
    }, 10000);
  }
});

window.addEventListener('appinstalled', (evt) => {
  console.log('a2hs installed');
});

if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true) {
  console.log('display-mode is standalone');
}

$(window).ready(function () {
  $("#search-verb")["autocomplete"]({
    source: Urls['conjugation:autocomplete'](),
    minLength: 1,
    focus: function (event, ui) {
      $("#search-verb").val(ui.item["verb"]);
      return false;
    },
    select: function (event, ui) {
      event.preventDefault();
      window.location.href = ui.item['url'];
    }
  })["data"]("ui-autocomplete")["_renderItem"] = function (a, b) {
    let liClass = '';
    if (b['isInfinitive']){
      liClass = 'is-infinitive'
    }else if(!b['isInfinitive']){
      liClass = 'is-not-infinitive'
    }
    return $(`<li class='${liClass}'>`)["data"]("ui-menu-item", b)["append"]("<a href='" + b["url"] + "'>" + b["html"] + "</a>")["appendTo"](a);
  };
});
