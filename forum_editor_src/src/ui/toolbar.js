import { EMOJIS } from '../emoji.js';

// Markup copied verbatim from the legacy editor (forum-editor-legacy.js
// buildUI), minus the old contenteditable div: the TipTap view is mounted in
// .forum-visual-host instead.
function wrapperHtml() {
  const emojiItemsHtml = EMOJIS.map(function (item) {
    return '<span class="forum-emoji-item" data-emoji="' + item.char + '" data-code="' + item.code + '" title="' + item.code + '">' + item.char + '</span>';
  }).join('');

  return [
    '<div class="forum-editor-wrapper">',
        '<div class="forum-editor-toolbar">',
            // Left Mode Switcher Block
            '<div class="forum-editor-mode-block">',
                '<div class="forum-mode-switch" title="Переключить режим: Визуальный / Markdown">',
                    '<span class="forum-mode-switch-btn visual active" data-mode="visual" title="Визуальный редактор (WYSIWYG)"><i class="fa fa-eye"></i></span>',
                    '<label class="forum-toggle-track" title="Переключить режим">',
                        '<input type="checkbox" class="forum-mode-checkbox" aria-label="Переключить Markdown / Визуальный">',
                        '<span class="forum-toggle-thumb"></span>',
                    '</label>',
                    '<span class="forum-mode-switch-btn markdown" data-mode="markdown" title="Исходный Markdown"><i class="fa fa-code"></i></span>',
                '</div>',
            '</div>',
            '<div class="forum-toolbar-divider"></div>',
            // Formatting & Insert Tools Block
            '<div class="forum-editor-tools-block">',
                // Inline text formatting
                '<div class="btn-group btn-group-sm" role="group">',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="bold" title="Жирный (**текст**, Ctrl+B)"><i class="fa fa-bold"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="italic" title="Курсив (_текст_, Ctrl+I)"><i class="fa fa-italic"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="underline" title="Подчеркнутый (^^текст^^, Ctrl+U)"><i class="fa fa-underline"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="strikethrough" title="Зачеркнутый (~~текст~~, Ctrl+Shift+X, Alt+Shift+5)"><i class="fa fa-strikethrough"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="mark" title="Выделение маркером (==текст==)"><i class="fa fa-pencil" style="background:#fff3cd;padding:1px 3px;border-radius:2px;"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="code" title="Код / блок кода (`код` в строке, ```блок``` для нескольких строк, Ctrl+Shift+M)"><i class="fa fa-code"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="kbd" title="Клавиша (++клавиша++)"><i class="fa fa-keyboard-o"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="superscript" title="Верхний индекс (^текст^)"><i class="fa fa-superscript"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="subscript" title="Нижний индекс (~текст~)"><i class="fa fa-subscript"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="removeFormat" title="Очистить форматирование (Ctrl+Shift+N, Ctrl+\\)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;"><path d="M5 6h14"></path><path d="M12 6v12"></path><line x1="4" y1="4" x2="20" y2="20" stroke="currentColor" stroke-width="2.2"></line></svg></button>',
                '</div>',
                // Structure / Block tools
                '<div class="btn-group btn-group-sm" role="group">',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h2" title="Подзаголовок (## Заголовок)"><strong>H2</strong></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h3" title="Подзаголовок (### Заголовок)"><strong>H3</strong></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="quote" title="Цитата (> текст, Ctrl+Shift+.)"><i class="fa fa-quote-left"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ul" title="Список (- пункт)"><i class="fa fa-list-ul"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ol" title="Нумерованный список (1. пункт)"><i class="fa fa-list-ol"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="spoiler" title="Спойлер (???- Заголовок, Ctrl+Shift+P)"><i class="fa fa-caret-square-o-down"></i></button>',
                '</div>',
                // Insert
                '<div class="btn-group btn-group-sm" role="group">',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="link" title="Вставить ссылку (Ctrl+K)"><i class="fa fa-link"></i></button>',
                    '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="image" title="Вставить или загрузить изображение"><i class="fa fa-picture-o"></i></button>',
                    '<div class="btn-group btn-group-sm forum-emoji-group position-relative" role="group">',
                        '<button type="button" class="btn btn-light forum-editor-btn forum-emoji-btn" title="Вставить эмодзи"><i class="fa fa-smile-o"></i></button>',
                        '<div class="forum-emoji-dropdown d-none">',
                            '<div class="forum-emoji-header">',
                                '<span class="small font-weight-bold text-muted">Эмодзи</span>',
                                '<button type="button" class="btn btn-sm btn-link text-muted p-0 forum-emoji-close" style="font-size:16px;line-height:1;text-decoration:none;">&times;</button>',
                            '</div>',
                            '<div class="forum-emoji-grid">' + emojiItemsHtml + '</div>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        // Hidden file input
        '<input type="file" class="forum-image-file-input d-none" accept="image/jpeg,image/png,image/gif,image/webp">',
        // Custom Modal Dialog Overlay for Link & Image Insertion
        '<div class="forum-editor-modal-overlay d-none">',
            '<div class="forum-editor-modal" role="dialog" aria-modal="true">',
                '<div class="forum-editor-modal-header">',
                    '<h5 class="forum-editor-modal-title">Вставить ссылку</h5>',
                    '<button type="button" class="forum-editor-modal-close" aria-label="Закрыть">&times;</button>',
                '</div>',
                '<div class="forum-editor-modal-body"></div>',
                '<div class="forum-editor-modal-footer">',
                    '<button type="button" class="btn btn-sm btn-secondary forum-editor-modal-cancel">Отмена</button>',
                    '<button type="button" class="btn btn-sm btn-primary forum-editor-modal-submit">Вставить</button>',
                '</div>',
            '</div>',
        '</div>',
        // Editor body container
        '<div class="forum-editor-container position-relative">',
            '<div class="forum-visual-host"></div>',
            // Drop overlay
            '<div class="forum-drop-overlay d-none">',
                '<div class="forum-drop-message">',
                    '<i class="fa fa-cloud-upload fa-3x mb-2 text-primary"></i>',
                    '<div><strong>Отпустите изображение для загрузки</strong></div>',
                    '<small class="text-muted">Файл будет оптимизирован и добавлен в сообщение</small>',
                '</div>',
            '</div>',
            // Upload progress banner
            '<div class="forum-upload-progress d-none alert alert-info py-2 px-3 mb-0">',
                '<i class="fa fa-spinner fa-spin mr-2"></i>',
                '<span class="upload-progress-text">Загрузка и оптимизация изображения...</span>',
            '</div>',
        '</div>',
        // Footer
        '<div class="forum-editor-footer d-flex justify-content-between align-items-center">',
            '<small class="text-muted"><i class="fa fa-info-circle mr-1"></i>Поддерживаются: Drag & Drop и Ctrl+V для картинок, <code>^^подчеркивание^^</code>, <code>==маркер==</code>, <code>~~зачеркивание~~</code>, <code>++клавиши++</code>, спойлеры.</small>',
            '<div class="d-flex align-items-center flex-shrink-0 ml-2">',
                '<small class="text-muted font-italic forum-char-counter mr-2"></small>',
                '<div class="forum-editor-resizer" title="Изменить высоту поля ввода">',
                    '<svg viewBox="0 0 10 10" width="10" height="10">',
                        '<path d="M9 1L1 9M9 5L5 9M9 9L9 9" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round"/>',
                    '</svg>',
                '</div>',
            '</div>',
        '</div>',
    '</div>'
  ].join('');
}

/**
 * Inserts the editor wrapper before `textarea`, moves the textarea into
 * `.forum-editor-container` and returns the DOM handles.
 */
export function buildEditorDom(textarea) {
  const tpl = document.createElement('div');
  tpl.innerHTML = wrapperHtml();
  const wrapper = tpl.firstElementChild;
  textarea.parentNode.insertBefore(wrapper, textarea);

  const q = function (sel) { return wrapper.querySelector(sel); };
  const container = q('.forum-editor-container');
  const visualHost = q('.forum-visual-host');
  container.appendChild(textarea);

  return {
    wrapper: wrapper,
    toolbar: q('.forum-editor-toolbar'),
    container: container,
    visualHost: visualHost,
    dropOverlay: q('.forum-drop-overlay'),
    uploadProgress: q('.forum-upload-progress'),
    fileInput: q('.forum-image-file-input'),
    charCounter: q('.forum-char-counter'),
    modal: {
      overlay: q('.forum-editor-modal-overlay'),
      title: q('.forum-editor-modal-title'),
      body: q('.forum-editor-modal-body'),
      submit: q('.forum-editor-modal-submit'),
      cancel: q('.forum-editor-modal-cancel'),
      close: q('.forum-editor-modal-close'),
    },
    emoji: {
      button: q('.forum-emoji-btn'),
      dropdown: q('.forum-emoji-dropdown'),
      grid: q('.forum-emoji-grid'),
      close: q('.forum-emoji-close'),
    },
    resizer: q('.forum-editor-resizer'),
  };
}
