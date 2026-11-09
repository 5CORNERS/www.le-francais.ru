# Инструкция для Антона: Адаптивная высота упражнений LearningApps (Zero-Scroll Auto-Resize)

## 1. Суть изменения
Ранее для всех упражнений LearningApps задавалась фиксированная высота iFrame (по умолчанию `500px` или из Wagtail-блока), из-за чего:
* в коротких упражнениях оставалось много пустого пространства;
* в длинных упражнениях (или на узких экранах смартфонов) внутри iFrame появлялся вертикальный скроллбар, мешавший drag & drop и ухудшавший мобильный опыт.

Теперь упражнения адаптируют свою высоту под реальный размер контента на лету без внутреннего скроллера.

---

## 2. Как это работает (Архитектура)
1. **Внутри iFrame (на стороне CDN `files.le-francais.ru`)**:
   В скрипт `AppClientServer.js` добавлен расчёт высоты содержимого (`document.body.scrollHeight`, контейнеры `#content`, `#cards`, `#wrapper` и т.д.) с защитой от положительной обратной связи (feedback loop cap). При изменении размеров и по таймеру iFrame отправляет родителю сообщение:
   ```javascript
   window.parent.postMessage({
     type: 'le_francais_la_resize',
     appId: AppID,
     frameHeight: calculatedHeight
   }, '*');
   ```
   *Все изменения на стороне CDN уже развёрнуты и полностью обратно совместимы.*

2. **На стороне сайта (`le-francais.ru`)**:
   Шаблон блока упражнений слушает эти сообщения и плавно выставляет `iframe.style.height`:
   ```javascript
   window.addEventListener('message', function(e) {
     if (!e.data || e.data.type !== 'le_francais_la_resize') return;
     // сопоставляем e.source или e.data.appId и выставляем iframe.style.height
   });
   ```
   Также при переключении вкладок урока (Bootstrap tab `shown.bs.tab`) родитель шлёт в скрытые iFrame сигнал `le_francais_request_resize`, чтобы они мгновенно обновили свою высоту при открытии.

---

## 3. Как применить изменения

### Вариант 1: Через GitHub Pull Request (Рекомендуется)
Открыт готовый пулл-реквест против ветки **`render`**:
👉 **[PR #79: feature/learning-apps-auto-resize](https://github.com/5CORNERS/www.le-francais.ru/pull/79)**

Вся правка в PR затрагивает ровно один файл: `home/templates/blocks/learning_apps_block.html`.

---

### Вариант 2: Вручную в один файл
Если удобнее перенести руками, нужно изменить только файл:
`home/templates/blocks/learning_apps_block.html`

Заменить его содержимое на следующий код:

```html
<h4 style='text-align: center;margin-bottom: 0;margin-top: 0.5rem'><b>
    {% if self.show_lesson_number %}{{ page.lesson_number }}.{% endif %}{{ self.number }}{% if not self.show_lesson_number %}.{% endif %} {{ self.title }}</b></h4>
<iframe src="https://files.le-francais.ru/learning-apps/{{ self.app_id }}/index.html"
        class="learning-apps-iframe"
        data-app-id="{{ self.app_id }}"
        style="border:0;width: {{ self.width }}; min-height: 280px; height: {{ self.height }}; transition: height 0.2s ease-out;" loading="lazy"></iframe>
<script>
if (!window._leFrancaisLaResizeInitialized) {
  window._leFrancaisLaResizeInitialized = true;
  window.addEventListener('message', function(e) {
    if (!e.data || e.data.type !== 'le_francais_la_resize') return;
    var iframes = document.querySelectorAll('iframe.learning-apps-iframe, iframe[src*="learning-apps"]');
    for (var i = 0; i < iframes.length; i++) {
      var iframe = iframes[i];
      if (iframe.contentWindow === e.source || (e.data.appId && iframe.src.indexOf(e.data.appId) !== -1)) {
        if (e.data.frameHeight && e.data.frameHeight > 100) {
          iframe.style.height = e.data.frameHeight + 'px';
        }
        break;
      }
    }
  });

  if (window.jQuery) {
    window.jQuery(document).on('shown.bs.tab', 'a[data-toggle="tab"]', function(e) {
      var target = window.jQuery(e.target.getAttribute('href'));
      if (target.length) {
        var iframes = target.find('iframe.learning-apps-iframe, iframe[src*="learning-apps"]');
        iframes.each(function() {
          try {
            this.contentWindow.postMessage({ type: 'le_francais_request_resize' }, '*');
          } catch(err) {}
        });
      }
    });
  }
}
</script>
```

---

## 4. Что нужно на проде
* Никаких миграций базы данных или перезапусков сервисов не требуется.
* На CDN ничего дополнительно заливать не нужно — всё уже работает.
* При мердже PR #79 изменения автоматически подхватятся при следующем деплое ветки `render` на Render.com.
