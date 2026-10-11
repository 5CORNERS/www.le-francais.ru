import { createForumEditor } from './editor.js';

function start() {
  if (window.forumEditor) return;
  const textarea = document.getElementById('id_body');
  if (!textarea) return;
  window.forumEditor = createForumEditor({ textarea: textarea, uploadUrl: '/forum/upload-image/' });
}

document.addEventListener('DOMContentLoaded', start);
