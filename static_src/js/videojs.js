import videojs from "!video.js";
import 'dashjs';
import 'videojs-contrib-eme';
// import 'videojs-contrib-quality-levels';
import 'videojs-contrib-quality-menu';

import ruLang from './videojs_lang/ru'
videojs.addLanguage('ru', ruLang);

window.videojs = videojs;
