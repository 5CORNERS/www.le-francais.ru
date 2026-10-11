import { describe, test, expect, beforeEach } from 'vitest';
import { initResizeHandle } from '../src/ui/resizeHandle.js';

let handle;
let target;
let cleanup;

function mouse(el, type, y) {
  el.dispatchEvent(new MouseEvent(type, { bubbles: true, clientY: y }));
}

function touch(el, type, y) {
  const ev = new Event(type, { bubbles: true, cancelable: true });
  ev.touches = type === 'touchend' || type === 'touchcancel' ? [] : [{ clientY: y }];
  el.dispatchEvent(ev);
}

beforeEach(() => {
  document.body.innerHTML = '<div id="h"></div><div id="t"></div><textarea id="x"></textarea>';
  handle = document.getElementById('h');
  target = document.getElementById('t');
  Object.defineProperty(target, 'offsetHeight', { configurable: true, value: 200 });
  cleanup = initResizeHandle(handle, () => [target]);
});

describe('initResizeHandle', () => {
  test('mouse drag grows the target by the pointer delta', () => {
    mouse(handle, 'mousedown', 100);
    expect(document.body.style.userSelect).toBe('none');
    mouse(document, 'mousemove', 160);
    expect(target.style.height).toBe('260px');
    expect(target.style.maxHeight).toBe('none');
    mouse(document, 'mouseup', 160);
    expect(document.body.style.userSelect).toBe('');
    mouse(document, 'mousemove', 400);
    expect(target.style.height).toBe('260px');
  });

  test('touch drag does the same', () => {
    touch(handle, 'touchstart', 100);
    touch(document, 'touchmove', 160);
    expect(target.style.height).toBe('260px');
    touch(document, 'touchend', 160);
    expect(document.body.style.userSelect).toBe('');
  });

  test('touchcancel ends the drag like touchend (final review 12)', () => {
    touch(handle, 'touchstart', 100);
    touch(document, 'touchmove', 160);
    touch(document, 'touchcancel', 160);
    expect(document.body.style.userSelect).toBe('');
    expect(document.documentElement.style.cursor).toBe('');
    touch(document, 'touchmove', 300);
    expect(target.style.height).toBe('260px');
  });

  test('height never drops below 140px', () => {
    mouse(handle, 'mousedown', 100);
    mouse(document, 'mousemove', -500);
    expect(target.style.height).toBe('140px');
    mouse(document, 'mouseup', 0);
  });

  test('cleanup removes the handle listeners', () => {
    cleanup();
    mouse(handle, 'mousedown', 100);
    mouse(document, 'mousemove', 160);
    expect(target.style.height).toBe('');
  });

  test('uses the visible target for the start height and sizes all targets', () => {
    const ta = document.getElementById('x');
    Object.defineProperty(ta, 'offsetHeight', { configurable: true, value: 300 });
    target.style.display = 'none';
    cleanup();
    cleanup = initResizeHandle(handle, () => [target, ta]);
    mouse(handle, 'mousedown', 0);
    mouse(document, 'mousemove', 10);
    expect(ta.style.height).toBe('310px');
    expect(target.style.height).toBe('310px');
    mouse(document, 'mouseup', 10);
  });
});
