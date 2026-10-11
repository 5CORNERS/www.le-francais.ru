import { createForumEditor } from './editor.js';

function start() {
  if (window.forumEditor) return;
  const textarea = document.getElementById('id_body');
  if (!textarea) return;
  try {
    window.forumEditor = createForumEditor({ textarea: textarea, uploadUrl: '/forum/upload-image/' });
  } catch (e) {
    // The plain textarea stays usable as the form field.
    console.error('forum-editor: cannot start the editor', e);
  }
}

// The bundle is loaded with `defer`: the DOM is usually parsed already.
if (document.readyState !== 'loading') start();
else document.addEventListener('DOMContentLoaded', start);
