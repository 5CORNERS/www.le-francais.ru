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
