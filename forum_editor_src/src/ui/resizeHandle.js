const MIN_HEIGHT = 140;

function isHidden(el) {
  return window.getComputedStyle(el).display === 'none';
}

/**
 * Drag handle that resizes the editor and textarea together (port of the legacy
 * initResizer). Returns a cleanup function.
 */
export function initResizeHandle(resizerEl, getTargets) {
  if (!resizerEl) return function () {};

  let active = null;

  function startResize(startY) {
    const targets = getTargets();
    const visible = targets.filter((t) => !isHidden(t))[0] || targets[0];
    const startHeight = visible ? visible.offsetHeight : MIN_HEIGHT;
    document.body.style.userSelect = 'none';
    document.documentElement.style.cursor = 'se-resize';

    function onMove(clientY) {
      const height = Math.max(MIN_HEIGHT, startHeight + clientY - startY) + 'px';
      targets.forEach((t) => {
        t.style.height = height;
        t.style.maxHeight = 'none';
      });
    }
    function onMouseMove(e) {
      onMove(e.clientY);
    }
    function onTouchMove(e) {
      if (e.touches && e.touches.length) onMove(e.touches[0].clientY);
    }
    function onEnd() {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onEnd);
      document.removeEventListener('touchmove', onTouchMove);
      document.removeEventListener('touchend', onEnd);
      document.documentElement.style.cursor = '';
      document.body.style.userSelect = '';
      active = null;
    }

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onEnd);
    document.addEventListener('touchmove', onTouchMove);
    document.addEventListener('touchend', onEnd);
    active = onEnd;
  }

  function onMouseDown(e) {
    e.preventDefault();
    startResize(e.clientY);
  }
  function onTouchStart(e) {
    if (e.touches && e.touches.length) startResize(e.touches[0].clientY);
  }

  resizerEl.addEventListener('mousedown', onMouseDown);
  resizerEl.addEventListener('touchstart', onTouchStart);

  return function cleanup() {
    resizerEl.removeEventListener('mousedown', onMouseDown);
    resizerEl.removeEventListener('touchstart', onTouchStart);
    if (active) active();
  };
}
