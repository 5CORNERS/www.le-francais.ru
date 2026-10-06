/**
 * ==========================================================================
 * Dictionary Component JS Module (django/standalone compatible)
 * ==========================================================================
 */

(function () {
  /**
   * Encodes a string to base64url format (UTF-8 safe).
   */
  function base64urlEncode(str) {
    try {
      return btoa(unescape(encodeURIComponent(str)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
    } catch (e) {
      return btoa(str)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
    }
  }

  /**
   * Formats text by replacing *text* with <mark>text</mark>.
   */
  function formatText(text) {
    if (!text) return '';
    return text
      .replace(/\*(.*?)\*/g, '<mark>$1</mark>')
      .replace(/<br\s*\/?>/gi, '<span style="display: block; margin-bottom: 0.5em;"></span>');
  }

  /**
   * Formats a comment text. If the comment was wrapped in outer markdown asterisks (*...*),
   * strips the outer pair so that only inner highlighted terms become <mark>.
   */
  function formatComment(text) {
    if (!text) return '';
    let str = text.trim();
    if (str.startsWith('*') && str.endsWith('*') && str.length > 2) {
      str = str.slice(1, -1).trim();
    }
    return formatText(str);
  }

  /**
   * Wraps an element into a smooth collapsible container for compact-view transitions.
   */
  function wrapCollapsible(childEl) {
    const wrapper = ce('div', 'dict-collapsible');
    const inner = ce('div', 'dict-collapsible-inner');
    inner.appendChild(childEl);
    wrapper.appendChild(inner);
    return wrapper;
  }

  /**
   * Helper to create an element with a class and optional content.
   */
  function ce(tag, className, html) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (html !== undefined) el.innerHTML = html;
    return el;
  }

  /**
   * Adjust example text wrapping layout on resize (legacy no-op)
   */
  window.updateExamplesWraps = function() {};

  /**
   * Renders a list of examples.
   */
  function renderExamples(examples) {
    const container = ce('div', 'examples-list');
    examples.forEach(function(ex) {
      if (!ex.fr && !ex.ru) return;
      const exampleEl = ce('div', 'example');
      const bulletSpan = ce('span', 'example-bullet', '“');
      bulletSpan.setAttribute('aria-hidden', 'true');
      const bodyEl = ce('div', 'example-body');

      if (ex.fr) {
        bodyEl.appendChild(ce('div', 'example-fr', formatText(ex.fr)));
      }
      if (ex.ru) {
        bodyEl.appendChild(ce('div', 'example-ru', formatText(ex.ru)));
      }

      exampleEl.appendChild(bulletSpan);
      exampleEl.appendChild(bodyEl);
      container.appendChild(exampleEl);
    });
    return container;
  }


  /**
   * Renders a meaning object.
   */
  function renderMeaning(meaning, index) {
    const el = ce('div', 'meaning');
    const inner = ce('div', 'meaning-inner');
    const descEl = ce('div', 'meaning-description');
    if (index !== undefined && index !== null) {
      const idxSpan = ce('span', 'meaning-index', index + '.');
      descEl.appendChild(idxSpan);
    }
    const textSpan = ce('span', 'meaning-text', formatText(meaning.description || ''));
    descEl.appendChild(textSpan);
    inner.appendChild(descEl);
    if (meaning.comment) {
      inner.appendChild(wrapCollapsible(ce('div', 'comment', formatComment(meaning.comment))));
    }
    if (meaning.examples && meaning.examples.length > 0) {
      inner.appendChild(wrapCollapsible(renderExamples(meaning.examples)));
    }
    el.appendChild(inner);
    return el;
  }

  /**
   * Renders a sense object (within phrases/idioms).
   */
  function renderSense(sense, parentTranslation) {
    const el = ce('div', 'sense');
    const hasDistinctDesc = Boolean(sense.description && sense.description.trim() !== parentTranslation.trim());
    if (hasDistinctDesc) {
      el.appendChild(ce('div', 'sense-description', formatText(sense.description)));
    }
    if (sense.comment) {
      el.appendChild(wrapCollapsible(ce('div', 'comment', formatComment(sense.comment))));
    }
    if (sense.examples && sense.examples.length > 0) {
      el.appendChild(wrapCollapsible(renderExamples(sense.examples)));
    }
    if (!hasDistinctDesc) {
      el.classList.add('sense-examples-only');
    }
    return el;
  }

  /**
   * Renders a phrase or idiom object.
   */
  function renderPhrase(item) {
    const el = ce('div', 'phrase');
    const inner = ce('div', 'phrase-inner');
    const header = ce('div', 'phrase-header');
    header.appendChild(ce('span', 'phrase-fr', formatText(item.phrase)));
    header.appendChild(ce('span', 'phrase-translation', '— ' + formatText(item.translation)));
    inner.appendChild(header);
    if (item.comment) {
      inner.appendChild(wrapCollapsible(ce('div', 'comment', formatComment(item.comment))));
    }
    if (item.senses && item.senses.length > 0) {
      const sensesList = ce('div', 'senses-list');
      item.senses.forEach(function(sense) {
        sensesList.appendChild(renderSense(sense, item.translation));
      });
      inner.appendChild(sensesList);
    }
    el.appendChild(inner);
    return el;
  }

  /**
   * Animate the scroll transition when sections are expanded or collapsed.
   */
  function animateSectionScroll(parent, btn, isExpanding, hiddenHeight) {
    const startTime = performance.now();
    const duration = 500; // Match CSS transition duration (500ms)
    
    // 1. Calculate sectionTop robustly
    let sectionTop = parent.getBoundingClientRect().top + window.pageYOffset;
    let sibling = parent.previousElementSibling;
    while (sibling) {
      if (sibling.tagName === 'H3' || sibling.tagName === 'H2' || sibling.classList.contains('alert')) {
        sectionTop = sibling.getBoundingClientRect().top + window.pageYOffset;
        break;
      }
      sibling = sibling.previousElementSibling;
    }
    
    // 2. Resolve refElement (for expanding logic)
    let refElement = null;
    const firstHidden = parent.querySelector('.hidden-item');
    if (firstHidden) {
      const allItems = Array.from(parent.querySelectorAll('.meaning, .group, .phrase-item, .phrase'));
      const idx = allItems.indexOf(firstHidden);
      if (idx > 0) {
        refElement = allItems[idx - 1];
      }
    }
    if (!refElement) {
      refElement = parent;
    }

    // 3. For Collapsing: pre-calculate target scroll Y to center button
    let targetScrollYForCollapse = null;
    const hHeight = hiddenHeight || 0;
    if (!isExpanding && hHeight > 0) {
      const initialScrollY = window.pageYOffset;
      const btnInitialTop = btn.getBoundingClientRect().top;
      
      // Absolute Y coordinate of the button when expanded
      const btnAbsoluteY = btnInitialTop + initialScrollY;
      
      // After collapsing, the button's absolute position on the page
      const finalBtnAbsoluteY = btnAbsoluteY - hHeight;
      
      // We want the button's final position on the screen to be roughly at the middle of the viewport
      const targetScreenTop = window.innerHeight / 2;
      
      // The desired scroll offset to achieve this centering is
      const desiredScrollY = finalBtnAbsoluteY - targetScreenTop;
      
      // Ensure we don't scroll past the top of the body or above the section title
      let targetScrollY = Math.max(desiredScrollY, sectionTop);
      if (targetScrollY < 0) {
        targetScrollY = 0;
      }
      
      // We only want to scroll UP.
      if (targetScrollY < initialScrollY) {
        targetScrollYForCollapse = targetScrollY;
      }
    }

    const initialScrollYForAnimation = window.pageYOffset;

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const currentScrollY = window.pageYOffset;
      
      if (isExpanding) {
        // 1. Expanding logic (continuous tracking)
        const refTop = refElement.getBoundingClientRect().top + window.pageYOffset;
        const btnCurrentY = btn.getBoundingClientRect().top + window.pageYOffset;
        
        const idealScrollY = btnCurrentY - window.innerHeight + btn.offsetHeight + 20;
        const maxScrollY = refTop - 10;
        
        const targetY = Math.min(idealScrollY, maxScrollY);
        
        if (targetY > currentScrollY) {
          window.scrollTo(0, targetY);
        }
      } else {
        // 2. Collapsing logic (deterministic smooth eased transition to our pre-calculated target Y)
        if (targetScrollYForCollapse !== null) {
          // cubic easeOut
          const ease = 1 - Math.pow(1 - progress, 3);
          const nextScrollY = initialScrollYForAnimation + (targetScrollYForCollapse - initialScrollYForAnimation) * ease;
          window.scrollTo(0, nextScrollY);
        }
      }
      
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }
    
    requestAnimationFrame(step);
  }

  /**
   * Renders a list with "show more" functionality.
   */
  function renderExpandableList(container, items, title, containerClass, isCompact) {
    if (!items || items.length === 0) return;
    
    container.appendChild(ce('h3', '', title));
    
    const listLimit = 6;
    const listThreshold = 7;
    const isCollapsedInit = items.length > listThreshold;
    const listContainer = ce('div', containerClass + (isCollapsedInit ? ' collapsed' : ''));
    let renderedCount = 0;
    items.forEach(function(item) {
      const itemEl = renderPhrase(item);
      if (isCollapsedInit && renderedCount >= listLimit) {
          itemEl.classList.add('hidden-item');
      }
      renderedCount++;
      listContainer.appendChild(itemEl);
    });
    
    container.appendChild(listContainer);
    
    if (isCollapsedInit) {
      const remainingCount = items.length - listLimit;
      const btn = ce('div', 'show-more-btn', 'Показать еще ' + remainingCount);
      btn.onclick = function() {
        const isExpanding = listContainer.classList.contains('collapsed');
        
        // Measure expanded height of hidden items before toggle if we are about to collapse
        let hiddenHeight = 0;
        if (!isExpanding) {
          const hiddenItems = listContainer.querySelectorAll('.hidden-item');
          hiddenItems.forEach(function(item) {
            hiddenHeight += item.offsetHeight;
          });
        }

        listContainer.classList.toggle('collapsed');
        btn.classList.toggle('expanded');
        btn.textContent = isExpanding ? 'Свернуть' : 'Показать еще ' + remainingCount;
        
        animateSectionScroll(listContainer, btn, isExpanding, hiddenHeight);
      };
      container.appendChild(btn);
    }
  }

  const STORAGE_KEY = 'dict_compact_view';

  function getCompactMode() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === null) {
        return true; // Default: compact view (examples hidden)
      }
      return saved === 'true';
    } catch (e) {
      return true;
    }
  }

  function setCompactMode(val) {
    try {
      localStorage.setItem(STORAGE_KEY, val ? 'true' : 'false');
    } catch (e) {
      // Ignore if localStorage unavailable
    }
  }

  function toggleCompactMode() {
    const isNowCompact = !getCompactMode();
    setCompactMode(isNowCompact);
    document.querySelectorAll('.dictionnaire').forEach(function(c) {
      if (isNowCompact) {
        c.classList.add('compact-view');
      } else {
        c.classList.remove('compact-view');
      }
      const toggleBtn = c.querySelector('.dict-toggle-btn');
      if (toggleBtn) {
        toggleBtn.className = 'dict-toggle-btn ' + (isNowCompact ? 'compact' : 'expanded');
        const iconSpan = toggleBtn.querySelector('.dict-toggle-icon');
        if (iconSpan) iconSpan.textContent = isNowCompact ? '💡' : '✕';
        const textSpan = toggleBtn.querySelector('.dict-toggle-text');
        if (textSpan) textSpan.textContent = isNowCompact ? 'Показать примеры и пояснения' : 'Скрыть примеры и пояснения';
      }
    });
  }

  function hasExamplesOrComments(data) {
    if (!data) return false;
    if (data.comment) return true;
    if (data.groups) {
      for (let i = 0; i < data.groups.length; i++) {
        const g = data.groups[i];
        if (g.meanings) {
          for (let j = 0; j < g.meanings.length; j++) {
            const m = g.meanings[j];
            if (m.comment || (m.examples && m.examples.length > 0)) return true;
          }
        }
      }
    }
    if (data.meanings) {
      for (let j = 0; j < data.meanings.length; j++) {
        const m = data.meanings[j];
        if (m.comment || (m.examples && m.examples.length > 0)) return true;
      }
    }
    if (data.phrases) {
      for (let i = 0; i < data.phrases.length; i++) {
        const p = data.phrases[i];
        if (p.comment) return true;
        if (p.senses) {
          for (let j = 0; j < p.senses.length; j++) {
            const s = p.senses[j];
            if (s.comment || (s.examples && s.examples.length > 0)) return true;
          }
        }
      }
    }
    if (data.idioms) {
      for (let i = 0; i < data.idioms.length; i++) {
        const p = data.idioms[i];
        if (p.comment) return true;
        if (p.senses) {
          for (let j = 0; j < p.senses.length; j++) {
            const s = p.senses[j];
            if (s.comment || (s.examples && s.examples.length > 0)) return true;
          }
        }
      }
    }
    return false;
  }

  /**
   * Renders the dictionary data into the container.
   */
  function renderDictionary(container, data, verbId) {
    container.innerHTML = ''; 
    
    const isMobile = container.closest('.translation_mobile') !== null;
    const hasTranslations = (data.groups && data.groups.length > 0) || 
                            (data.phrases && data.phrases.length > 0) || 
                            (data.idioms && data.idioms.length > 0);
    
    // 1. Verb Header
    const verbUpper = data.verb.toUpperCase();
    const titleText = data.verb.length <= 15 ? "Перевод глагола " + verbUpper : "Перевод " + verbUpper;
    container.appendChild(ce('h2', '', titleText));

    const hasDetails = hasExamplesOrComments(data);
    const isCompact = hasDetails && getCompactMode();

    if (isCompact) {
      container.classList.add('compact-view');
    } else {
      container.classList.remove('compact-view');
    }

    // 1.2 Toggle Button (placed directly under H2, above notice plate)
    if (hasDetails) {
      const toggleBtn = ce('button', 'dict-toggle-btn ' + (isCompact ? 'compact' : 'expanded'));
      toggleBtn.type = 'button';
      const iconSpan = ce('span', 'dict-toggle-icon', isCompact ? '💡' : '✕');
      const textSpan = ce('span', 'dict-toggle-text', isCompact ? 'Показать примеры и пояснения' : 'Скрыть примеры и пояснения');
      toggleBtn.appendChild(iconSpan);
      toggleBtn.appendChild(textSpan);
      toggleBtn.onclick = function() {
        toggleCompactMode();
      };
      container.appendChild(toggleBtn);
    }

    // 1.5 Moderation Status Plates (Show community notice only if unverified)

      if (data.moderationStatus === 'draft' || data.moderationStatus === 'pending') {
        const noticeAlert = ce('div', 'alert alert-light', '');
        noticeAlert.style.padding = '8px 12px';
        noticeAlert.style.marginBottom = '15px';
        noticeAlert.style.border = '1px solid #ddd';
        noticeAlert.style.backgroundColor = '#f8f9fa';
        
        const noticeText = document.createTextNode('Этот раздел нам помогают создавать участники сообщества, он может содержать неточности. Заметили ошибку? ');
        const noticeLink = ce('a', '', 'Помогите ее исправить!');
        const encodedVerbIdForLink = base64urlEncode(verbId);
        noticeLink.href = 'https://coverbe.web.app/' + encodedVerbIdForLink;
        noticeLink.target = '_blank';
        
        noticeAlert.appendChild(noticeText);
        noticeAlert.appendChild(noticeLink);
        container.appendChild(noticeAlert);
      }


    // 2. Groups or Flat Meanings
    let totalMeanings = 0;
    if (data.groups && data.groups.length > 0) {
      data.groups.forEach(function(g) {
        if (g.meanings) totalMeanings += g.meanings.length;
      });
    } else if (data.meanings) {
      totalMeanings = data.meanings.length;
    }

    const meaningsLimit = 6;
    const meaningsThreshold = 7;

    let meaningsParent = container;
    let isMeaningsCollapsed = false;
    let remainingMeanings = 0;
    
    if (totalMeanings > meaningsThreshold) {
        isMeaningsCollapsed = true;
        remainingMeanings = totalMeanings - meaningsLimit;
        meaningsParent = ce('div', 'meanings-container collapsed');
    }

    let renderedCount = 0;

    if (data.groups && data.groups.length > 0) {
      const hasAnyGroupWithMultiple = Boolean(data.groups.some(function(g) {
        return g.meanings && g.meanings.length > 1;
      }));
      data.groups.forEach(function(group) {
        const groupEl = ce('div', 'group');
        const groupInner = ce('div', 'group-inner');
        
        // Check if group has a valid header to show
        const hasHeader = (group.romanNumeral && String(group.romanNumeral).trim() !== '') || 
                          (group.title && String(group.title).trim() !== '');
        
        if (hasHeader) {
          const header = ce('div', 'group-header');
          const headerInner = ce('div', 'group-header-inner');
          if (group.romanNumeral) {
            headerInner.appendChild(ce('span', 'roman-numeral', group.romanNumeral));
          }
          if (group.title) {
            headerInner.appendChild(ce('span', 'group-title', formatText(group.title)));
          }
          header.appendChild(headerInner);
          groupInner.appendChild(header);
        } else {
          groupEl.classList.add('no-header');
        }

        let groupFullyHidden = true;

        if (group.meanings && group.meanings.length > 0) {
          const meaningsList = ce('div', 'meanings-list');
          const shouldNumber = hasAnyGroupWithMultiple || group.meanings.length > 1;
          group.meanings.forEach(function(m, idx) {
            const mEl = renderMeaning(m, shouldNumber ? idx + 1 : null);
            if (isMeaningsCollapsed && renderedCount >= meaningsLimit) {
                mEl.classList.add('hidden-item');
            } else {
                groupFullyHidden = false;
            }
            meaningsList.appendChild(mEl);
            renderedCount++;
          });
          groupInner.appendChild(meaningsList);
        }

        groupEl.appendChild(groupInner);

        if (isMeaningsCollapsed && groupFullyHidden) {
            groupEl.classList.add('hidden-item');
        }

        meaningsParent.appendChild(groupEl);
      });
    } else if (data.meanings && data.meanings.length > 0) {
      const flatList = ce('div', 'meanings-list flat');
      const hasMultiple = data.meanings.length > 1;
      data.meanings.forEach(function(m, idx) {
        const mEl = renderMeaning(m, hasMultiple ? idx + 1 : null);
        if (isMeaningsCollapsed && renderedCount >= meaningsLimit) {
            mEl.classList.add('hidden-item');
        }
        flatList.appendChild(mEl);
        renderedCount++;
      });
      meaningsParent.appendChild(flatList);
    }

    if (isMeaningsCollapsed) {
        container.appendChild(meaningsParent);
        const btn = ce('div', 'show-more-btn', 'Показать еще ' + remainingMeanings);
        btn.onclick = function() {
          const isExpanding = meaningsParent.classList.contains('collapsed');
          
          // Measure expanded height of hidden items before toggle if we are about to collapse
          let hiddenHeight = 0;
          if (!isExpanding) {
            const hiddenItems = meaningsParent.querySelectorAll('.hidden-item');
            hiddenItems.forEach(function(item) {
              hiddenHeight += item.offsetHeight;
            });
          }

          meaningsParent.classList.toggle('collapsed');
          btn.classList.toggle('expanded');
          btn.textContent = isExpanding ? 'Свернуть' : 'Показать еще ' + remainingMeanings;
          
          animateSectionScroll(meaningsParent, btn, isExpanding, hiddenHeight);
        };
        container.appendChild(btn);
    }

    // 3. Phrases
    renderExpandableList(container, data.phrases, 'Фразеология', 'phrases-container', isCompact);

    // 4. Idioms
    renderExpandableList(container, data.idioms, 'Идиоматические выражения', 'idioms-container', isCompact);

    // 5. Postscript Comment (Desktop only, shown at the very end of section)
    if (data.comment) {
      const commentEl = ce('div', 'verb-article-comment', formatComment(data.comment));
      container.appendChild(wrapCollapsible(commentEl));
    }
  }

  /**
   * Main initialization function for any containers matching dictionnaire selector
   */
  async function init() {
    const containers = document.querySelectorAll('.dictionnaire');
    if (containers.length === 0) return;

    // Process each container independently, supporting custom data attributes
    containers.forEach(async function (container) {
      // 1. Determine active verb
      let verbId = container.getAttribute('data-verb');
      
      if (!verbId) {
        const urlParams = new URLSearchParams(window.location.search);
        verbId = urlParams.get('verb');
      }

      if (!verbId) {
        try {
          const configRes = await fetch('/api/config/verb');
          if (configRes.ok) {
            const configData = await configRes.json();
            if (configData.verbId) {
              verbId = configData.verbId;
            }
          }
        } catch (e) {
          console.log('Dictionary Module: Could not fetch verb from server config, falling back.');
        }
      }

      if (!verbId) {
        verbId = 'etre'; // Fallback default
      }

      // 2. Put container in Loading state
      container.innerHTML = '<div class="loading">Загрузка статьи...</div>';

      const encodedVerbId = base64urlEncode(verbId);

      const hideUI = () => {
        container.innerHTML = '';
      };

      // 3. Main API fetch with custom base URL option
      const apiBase = container.getAttribute('data-api-base') || '/api/';
      const apiUrl = apiBase.endsWith('/') ? (apiBase + encodedVerbId) : (apiBase + '/' + encodedVerbId);
      
      console.log('Dictionary Module: Fetching verb via: ' + apiUrl);

      const controller = new AbortController();
      const timeoutId = setTimeout(function() { 
        console.log('Dictionary Module: Request timed out');
        controller.abort(); 
      }, 10000);

      try {
        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        console.log('Dictionary Module: API Response Status:', response.status);

        if (response.status === 200) {
          const data = await response.json();
          container._dictData = data;
          container._dictVerbId = verbId;
          renderDictionary(container, data, verbId);
        } else {
          hideUI();
        }
      } catch (error) {
        clearTimeout(timeoutId);
        console.error('Dictionary Module: Fetch failed', error);
        hideUI();
      }
    });
  }

  // Bind to ready state or initialize immediately
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
