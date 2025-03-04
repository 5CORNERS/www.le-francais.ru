import * as lang from '../../node_modules/video.js/dist/lang/ru.json'

let extendedLang = {
    ...lang,
    ...{
        "Auto": "Авто",
        "Standard Definition": "Standard Definition",
        "High Definition": "High Definition",
        "SD": "SD",
        "HD": "HD",
        "4K": "4K",
        "Quality Levels": "Качество",
        "{1}, selected": "Выбрано {1}"
    }
}

export default extendedLang;
