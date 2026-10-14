import CodeBlock from '@tiptap/extension-code-block';

export const ForumCodeBlock = CodeBlock.configure({
  HTMLAttributes: { class: 'editor-code-block' },
  languageClassPrefix: 'language-',
});
