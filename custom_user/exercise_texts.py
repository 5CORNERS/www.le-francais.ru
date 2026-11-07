import os
import re
import json
import urllib.parse
from collections import OrderedDict
from django.conf import settings

TABLE_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'all_learning_apps_table.txt')
CACHE_APPS_DIR = os.path.join(settings.BASE_DIR, 'home', 'data', 'learning_apps_cache', 'apps')
SUGGESTIONS_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'exercise_text_suggestions.json')
REMOTE_BASE = '/var/www/www-root/data/www/files.le-francais.ru/learning-apps'


def load_suggestions():
    if os.path.exists(SUGGESTIONS_PATH):
        try:
            with open(SUGGESTIONS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _extract_text_param(initparams, param_name):
    for pair in initparams.split('&'):
        idx = pair.find('=')
        if idx != -1 and pair[:idx] == param_name:
            val = urllib.parse.unquote(pair[idx+1:])
            if val.startswith('text|'):
                val = val[5:]
            if val.endswith('|'):
                val = val[:-1]
            return val
    return ''


def get_all_lessons_summary():
    """
    Returns a sorted list of dicts: [{'lesson': 1, 'count': 5, 'sugg_count': 3}, ...]
    based on home/data/all_learning_apps_table.txt and exercise_text_suggestions.json
    """
    if not os.path.exists(TABLE_PATH):
        return []

    suggs = load_suggestions()
    lesson_sugg_counts = {}
    for aid, s_data in suggs.items():
        les = s_data.get('lesson')
        field_count = len(s_data.get('suggestions', {}))
        if les is not None and field_count > 0:
            lesson_sugg_counts[les] = lesson_sugg_counts.get(les, 0) + field_count

    counts = OrderedDict()
    with open(TABLE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[0].isdigit():
                les = int(parts[0])
                counts[les] = counts.get(les, 0) + 1

    return [{
        'lesson': k,
        'count': v,
        'sugg_count': lesson_sugg_counts.get(k, 0)
    } for k, v in sorted(counts.items())]


def get_lesson_exercises_data(lesson_num):
    """
    Returns list of exercise objects for a given lesson number:
    [
      {
        'id': 'pmbcn1vs519',
        'lesson': 29,
        'number': 4,
        'num_display': '29.4',
        'app_id': 'pmbcn1vs519',
        'title': '029.4.',
        'tool': '40',
        'tasktext': '...',
        'helptext': '...',
        'feedback': '...'
      }, ...
    ]
    """
    if not os.path.exists(TABLE_PATH):
        return []

    matched = []
    with open(TABLE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[0].isdigit() and int(parts[0]) == int(lesson_num):
                matched.append((int(parts[0]), int(parts[1]), parts[2].strip()))

    matched.sort(key=lambda x: x[1])

    suggestions_data = load_suggestions()

    exercises = []
    for les, num, app_id in matched:
        index_path = os.path.join(CACHE_APPS_DIR, app_id, 'index.html')
        tasktext = ''
        helptext = ''
        feedback = ''
        titel = ''
        untertitel = ''
        title = f"{les}.{num}."
        tool = ''

        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                m = re.search(r'var AppClientAppData\s*=\s*(\{.*?\});', content, re.DOTALL)
                if m:
                    data = json.loads(m.group(1))
                    tasktext = data.get('tasktext') or ''
                    helptext = data.get('helptext') or ''
                    title = data.get('title') or title
                    tool = data.get('tool') or ''

                    # Extract feedback from initparameters or top-level key
                    initparams = data.get('initparameters') or ''
                    fb_match = re.search(r'(?:^|&)feedback=([^&]*)', initparams)
                    if fb_match:
                        feedback = urllib.parse.unquote(fb_match.group(1))
                    elif data.get('feedback'):
                        feedback = data.get('feedback') or ''

                    titel = _extract_text_param(initparams, 'titel')
                    untertitel = _extract_text_param(initparams, 'untertitel')
            except Exception as e:
                tasktext = f"[Ошибка чтения данных: {e}]"

        exercises.append({
            'id': app_id,
            'lesson': les,
            'number': num,
            'num_display': f"{les}.{num}",
            'app_id': app_id,
            'title': title,
            'tool': tool,
            'tasktext': tasktext,
            'helptext': helptext,
            'feedback': feedback,
            'titel': titel,
            'untertitel': untertitel,
            'suggestions': suggestions_data.get(app_id, {}).get('suggestions', {}),
        })

    return exercises


def save_exercise_text(app_id, field, value):
    """
    Updates local index.html and uploads it to files.le-francais.ru via SFTP.
    field must be one of: 'tasktext', 'helptext', 'feedback', 'titel', 'untertitel'
    """
    if field not in ('tasktext', 'helptext', 'feedback', 'titel', 'untertitel'):
        raise ValueError(f"Unknown field: {field}")

    index_path = os.path.join(CACHE_APPS_DIR, app_id, 'index.html')
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Local exercise file not found: {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    m = re.search(r'(var AppClientAppData\s*=\s*)(\{.*?\})(;)', content, re.DOTALL)
    if not m:
        raise ValueError("AppClientAppData JSON block not found in index.html")

    prefix, json_str, suffix = m.group(1), m.group(2), m.group(3)
    data = json.loads(json_str)

    if field == 'tasktext':
        data['tasktext'] = value
    elif field == 'helptext':
        data['helptext'] = value
    elif field == 'feedback':
        data['feedback'] = value
        # Also update initparameters
        initparams = data.get('initparameters') or ''
        quoted_val = urllib.parse.quote(value)
        if re.search(r'(?:^|&)feedback=[^&]*', initparams):
            new_init = re.sub(r'((?:^|&)feedback=)[^&]*', r'\g<1>' + quoted_val, initparams)
        else:
            sep = '&' if initparams and not initparams.endswith('&') else ''
            new_init = initparams + f"{sep}feedback={quoted_val}"
        data['initparameters'] = new_init
    elif field in ('titel', 'untertitel'):
        initparams = data.get('initparameters') or ''
        pairs = initparams.split('&')
        found = False
        new_pairs = []
        encoded_val = f"text|{urllib.parse.quote(value)}|"
        for pair in pairs:
            if not pair:
                continue
            idx = pair.find('=')
            if idx != -1 and pair[:idx] == field:
                new_pairs.append(f"{field}={encoded_val}")
                found = True
            else:
                new_pairs.append(pair)
        if not found:
            new_pairs.append(f"{field}={encoded_val}")
        data['initparameters'] = '&'.join(new_pairs)

    new_json_str = json.dumps(data, ensure_ascii=False)
    new_content = content[:m.start(2)] + new_json_str + content[m.end(2):]

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Now upload to SFTP
    sftp_synced = False
    sftp_error = None
    try:
        host = os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME')
        user = os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME')
        passwd = os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD')

        if host and user and passwd:
            import pysftp
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(host=host, username=user, password=passwd, cnopts=cnopts) as sftp:
                remote_dest = f"{REMOTE_BASE}/{app_id}/index.html"
                sftp.put(index_path, remote_dest)
                sftp_synced = True
    except Exception as e:
        sftp_error = str(e)

    return {
        'status': 'ok',
        'app_id': app_id,
        'field': field,
        'sftp_synced': sftp_synced,
        'sftp_error': sftp_error
    }


def save_exercise_texts_batch(items):
    """
    items: list of dicts [{'app_id': ..., 'field': ..., 'value': ...}]
    Groups changes by app_id so each local index.html is updated once,
    then uploads all changed files to SFTP in a single connection session.
    """
    if not items:
        return {'status': 'ok', 'saved_count': 0, 'sftp_synced': False}

    apps_updates = {}
    for it in items:
        app_id = it.get('app_id')
        field = it.get('field')
        value = it.get('value', '')
        if not app_id or field not in ('tasktext', 'helptext', 'feedback', 'titel', 'untertitel'):
            continue
        apps_updates.setdefault(app_id, {})[field] = value

    saved_app_ids = []
    for app_id, field_dict in apps_updates.items():
        index_path = os.path.join(CACHE_APPS_DIR, app_id, 'index.html')
        if not os.path.exists(index_path):
            continue

        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        m = re.search(r'(var AppClientAppData\s*=\s*)(\{.*?\})(;)', content, re.DOTALL)
        if not m:
            continue

        prefix, json_str, suffix = m.group(1), m.group(2), m.group(3)
        data = json.loads(json_str)

        for field, value in field_dict.items():
            if field == 'tasktext':
                data['tasktext'] = value
            elif field == 'helptext':
                data['helptext'] = value
            elif field == 'feedback':
                data['feedback'] = value
                initparams = data.get('initparameters') or ''
                quoted_val = urllib.parse.quote(value)
                if re.search(r'(?:^|&)feedback=[^&]*', initparams):
                    new_init = re.sub(r'((?:^|&)feedback=)[^&]*', r'\g<1>' + quoted_val, initparams)
                else:
                    sep = '&' if initparams and not initparams.endswith('&') else ''
                    new_init = initparams + f"{sep}feedback={quoted_val}"
                data['initparameters'] = new_init
            elif field in ('titel', 'untertitel'):
                initparams = data.get('initparameters') or ''
                pairs = initparams.split('&')
                found = False
                new_pairs = []
                encoded_val = f"text|{urllib.parse.quote(value)}|"
                for pair in pairs:
                    if not pair:
                        continue
                    idx = pair.find('=')
                    if idx != -1 and pair[:idx] == field:
                        new_pairs.append(f"{field}={encoded_val}")
                        found = True
                    else:
                        new_pairs.append(pair)
                if not found:
                    new_pairs.append(f"{field}={encoded_val}")
                data['initparameters'] = '&'.join(new_pairs)

        new_json_str = json.dumps(data, ensure_ascii=False)
        new_content = content[:m.start(2)] + new_json_str + content[m.end(2):]

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        saved_app_ids.append(app_id)

    # SFTP upload all modified files in a single connection
    sftp_synced = False
    sftp_error = None
    try:
        host = os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME')
        user = os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME')
        passwd = os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD')

        if host and user and passwd and saved_app_ids:
            import pysftp
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(host=host, username=user, password=passwd, cnopts=cnopts) as sftp:
                for app_id in saved_app_ids:
                    remote_dest = f"{REMOTE_BASE}/{app_id}/index.html"
                    local_path = os.path.join(CACHE_APPS_DIR, app_id, 'index.html')
                    sftp.put(local_path, remote_dest)
            sftp_synced = True
    except Exception as e:
        sftp_error = str(e)

    return {
        'status': 'ok',
        'saved_count': len(saved_app_ids),
        'saved_app_ids': saved_app_ids,
        'sftp_synced': sftp_synced,
        'sftp_error': sftp_error
    }
