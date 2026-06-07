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
   * Helper to create an element with a class and optional content.
   */
  function ce(tag, className, html) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (html !== undefined) el.innerHTML = html;
    return el;
  }

  /**
   * Adjust example text wrapping layout on resize
   */
  window.updateExamplesWraps = function() {
    document.querySelectorAll('.example').forEach(function(ex) {
      const fr = ex.querySelector('.example-fr');
      const ru = ex.querySelector('.example-ru');
      if (!fr || !ru || ex.offsetParent === null) return;
      
      // Remove wrapped class initially to accurately measure natural flow
      ru.classList.remove('wrapped');
      
      // Wait for layout to update
      const frRect = fr.getBoundingClientRect();
      const ruRect = ru.getBoundingClientRect();
      if (ruRect.bottom > frRect.bottom + 5) {
        ru.classList.add('wrapped');
      }
    });
  };
  window.addEventListener('resize', window.updateExamplesWraps);

  /**
   * Renders a list of examples.
   */
  function renderExamples(examples) {
    const container = ce('div', 'examples-list');
    examples.forEach(function(ex) {
      const exampleEl = ce('div', 'example');
      const frSpan = ce('span', 'example-fr', formatText(ex.fr));
      const ruSpan = ce('span', 'example-ru', formatText(ex.ru));
      exampleEl.appendChild(frSpan);
      exampleEl.appendChild(ruSpan);
      container.appendChild(exampleEl);
      
      setTimeout(window.updateExamplesWraps, 0);
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
    const textSpan = ce('span', '', formatText(meaning.description || ''));
    descEl.appendChild(textSpan);
    inner.appendChild(descEl);
    if (meaning.comment) {
      inner.appendChild(ce('div', 'comment', formatText(meaning.comment)));
    }
    if (meaning.examples && meaning.examples.length > 0) {
      inner.appendChild(renderExamples(meaning.examples));
    }
    el.appendChild(inner);
    return el;
  }

  /**
   * Renders a sense object (within phrases/idioms).
   */
  function renderSense(sense, parentTranslation) {
    const el = ce('div', 'sense');
    if (sense.description && sense.description.trim() !== parentTranslation.trim()) {
      el.appendChild(ce('div', 'sense-description', formatText(sense.description)));
    }
    if (sense.comment) {
      el.appendChild(ce('div', 'comment', formatText(sense.comment)));
    }
    if (sense.examples && sense.examples.length > 0) {
      el.appendChild(renderExamples(sense.examples));
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
      inner.appendChild(ce('div', 'comment', formatText(item.comment)));
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
  function renderExpandableList(container, items, title, containerClass) {
    if (!items || items.length === 0) return;
    
    container.appendChild(ce('h3', '', title));
    
    const isCollapsedInit = items.length > 6;
    const listContainer = ce('div', containerClass + (isCollapsedInit ? ' collapsed' : ''));
    let renderedCount = 0;
    items.forEach(function(item) {
      const itemEl = renderPhrase(item);
      if (isCollapsedInit && renderedCount >= 4) {
          itemEl.classList.add('hidden-item');
      }
      renderedCount++;
      listContainer.appendChild(itemEl);
    });
    
    container.appendChild(listContainer);
    
    if (isCollapsedInit) {
      const remainingCount = items.length - 4;
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

    // 1.5 Moderation Status Plates (Show community notice only if unverified)

      if (data.moderationStatus === 'draft' || data.moderationStatus === 'pending') {
        const noticeAlert = ce('div', 'alert alert-light', '');
        noticeAlert.style.fontSize = '14px';
        noticeAlert.style.padding = '8px 12px';
        noticeAlert.style.marginBottom = '15px';
        noticeAlert.style.border = '1px solid #ddd';
        noticeAlert.style.backgroundColor = '#f8f9fa';
        
        const noticeText = document.createTextNode('Этот раздел нам помогают создавать участниками сообщества, он может содержать неточности. Заметили ошибку? ');
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

    let meaningsParent = container;
    let isMeaningsCollapsed = false;
    let remainingMeanings = 0;
    
    if (totalMeanings > 5) {
        isMeaningsCollapsed = true;
        remainingMeanings = totalMeanings - 4;
        meaningsParent = ce('div', 'meanings-container collapsed');
    }

    let renderedCount = 0;

    if (data.groups && data.groups.length > 0) {
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
          const hasMultiple = group.meanings.length > 1;
          group.meanings.forEach(function(m, idx) {
            const mEl = renderMeaning(m, hasMultiple ? idx + 1 : null);
            if (isMeaningsCollapsed && renderedCount >= 4) {
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
        if (isMeaningsCollapsed && renderedCount >= 4) {
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
    renderExpandableList(container, data.phrases, 'Фразеология', 'phrases-container');

    // 4. Idioms
    renderExpandableList(container, data.idioms, 'Идиоматические выражения', 'idioms-container');

    // 5. Postscript Comment (Desktop only, shown at the very end of section)
    if (data.comment) {
      const commentEl = ce('div', 'verb-article-comment', formatText(data.comment));
      container.appendChild(commentEl);
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
