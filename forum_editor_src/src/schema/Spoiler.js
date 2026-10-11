import { Node } from '@tiptap/core';

export const Spoiler = Node.create({
  name: 'spoiler',
  group: 'block',
  content: 'spoilerSummary spoilerBody',
  defining: true,
  isolating: true,
  parseHTML() {
    return [{ tag: 'details' }];
  },
  renderHTML() {
    return ['details', { class: 'forum-spoiler', open: '' }, 0];
  },
});

export const SpoilerSummary = Node.create({
  name: 'spoilerSummary',
  content: 'inline*',
  defining: true,
  parseHTML() {
    return [{ tag: 'summary' }];
  },
  renderHTML() {
    return ['summary', 0];
  },
});

export const SpoilerBody = Node.create({
  name: 'spoilerBody',
  content: 'block+',
  defining: true,
  parseHTML() {
    return [{ tag: 'div.spoiler-body' }];
  },
  renderHTML() {
    return ['div', { class: 'spoiler-body' }, 0];
  },
});
