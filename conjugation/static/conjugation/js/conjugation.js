let deferredPrompt;
let installPromptShown = false;
let $searchVerb;

const INSTALL_PROMPT_STORAGE_KEY = 'conjugation_install_prompt_shown';

function hasSeenInstallPrompt() {
  return localStorage.getItem(INSTALL_PROMPT_STORAGE_KEY) === '1';
}

function markInstallPromptSeen() {
  localStorage.setItem(INSTALL_PROMPT_STORAGE_KEY, '1');
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/static/conjugation/js/conjugation-sw.js', {
      'scope': '/conjugaison/'
    }).then(function (registration) {
      // Registration was successful
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function (err) {
      // registration failed :(
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}

window.addEventListener('beforeinstallprompt', function (e) {
  e.preventDefault();
  deferredPrompt = e;
});

function tryShowInstallPrompt() {
  if (installPromptShown || !deferredPrompt || hasSeenInstallPrompt()) return;

  installPromptShown = true;
  markInstallPromptSeen();

  deferredPrompt.prompt();
  deferredPrompt.userChoice.finally(() => {
    deferredPrompt = null;
  });
}

window.addEventListener('pointerdown', tryShowInstallPrompt, { once: true });
window.addEventListener('keydown', tryShowInstallPrompt, { once: true });

window.addEventListener('appinstalled', (evt) => {
  console.log('a2hs installed');
});

if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true) {
  console.log('display-mode is standalone');
}

$(window).ready(function () {
  function showHiddenAutocomplete() {
    $('.load-more.hide').slideDown(500).removeClass('hide').addClass('show');
    $('.load-more.action').remove()
  }


    $searchVerb = $("#search-verb").autocomplete({
      source: Urls['conjugation:autocomplete'](),
      minLength: 0,
      focus: function (event, ui) {
        if (event.originalEvent.originalEvent.type === 'keydown') {
          $("#search-verb").val(ui.item["verb"]);
        }
        if (ui.item['cls'].includes('hide')) {
          showHiddenAutocomplete()
        }
        return false;
      },
      select: function (event, ui) {
        event.preventDefault();
        window.location.href = ui.item['url'];
      },
      open: function (event, ui) {
        $('.ui-menu').width($('#search-verb').innerWidth()).css('max-height', $(window).height() - $('#search-verb').offset().top - $('#search-verb').height() - 20);
        if ($('.load-more.hide').length) {
          $('.ui-autocomplete').append($("<li class='verb-autocomplete-item ui-menu-item load-more action'><a class='ui-menu-item-wrapper'>Показать ещё</a></li>").on('click', event => {
            showHiddenAutocomplete()
          }));
          $('.ui-autocomplete.hide').on('focus', event => {
            showHiddenAutocomplete();
          })
        }
      },
      search: function (event, ui) {
        if (event.target.value === ""){
          $searchVerb.autocomplete('option', 'source', [
            {
              "url": "/conjugaison/etre/",
              "verb": "être",
              "html": "<b></b>être",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/avoir/",
              "verb": "avoir",
              "html": "<b></b>avoir",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/aller/",
              "verb": "aller",
              "html": "<b></b>aller",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/faire/",
              "verb": "faire",
              "html": "<b></b>faire",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/venir/",
              "verb": "venir",
              "html": "<b></b>venir",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/prendre/",
              "verb": "prendre",
              "html": "<b></b>prendre",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/appeler/",
              "verb": "appeler",
              "html": "<b></b>appeler",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/pouvoir/",
              "verb": "pouvoir",
              "html": "<b></b>pouvoir",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/vouloir/",
              "verb": "vouloir",
              "html": "<b></b>vouloir",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/voir/",
              "verb": "voir",
              "html": "<b></b>voir",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/partir/",
              "verb": "partir",
              "html": "<b></b>partir",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/mettre/",
              "verb": "mettre",
              "html": "<b></b>mettre",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
            {
              "url": "/conjugaison/dire/",
              "verb": "dire",
              "html": "<b></b>dire",
              "isInfinitive": true,
              "cls": "starts-with-infinitive"
            },
          ]);
        }else{
          $searchVerb.autocomplete('option', 'source', Urls['conjugation:autocomplete']());
        }
      }
    });
    $searchVerb.data('ui-autocomplete')._renderItem = function (a, b) {
      let liClass = '';
      if (b['isInfinitive']) {
        liClass = 'is-infinitive'
      } else if (!b['isInfinitive']) {
        liClass = 'is-not-infinitive'
      }
      return $(`<li class='verb-autocomplete-item ${liClass} ${b["cls"]}'>`
      )["data"]("ui-menu-item", b)["append"]("<a href='" + b["url"] + "'>" + b["html"] + "</a>")["appendTo"](a);
    };
    $searchVerb.on('focus', e=>{
      $searchVerb.autocomplete('search', e.target.value);
    })
});
