# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'le_francais.settings.dev')

import django
django.setup()

from custom_user.exercise_texts import get_lesson_exercises_data, get_all_lessons_summary
from custom_user.exercise_proofreader import proofread_text, build_inline_diff_html

SUGGESTIONS_PATH = os.path.join('home', 'data', 'exercise_text_suggestions.json')


def main():
    print("Scanning lessons 1..150 for proofreading suggestions...")
    summary = get_all_lessons_summary()
    target_lessons = [x['lesson'] for x in summary if 1 <= x['lesson'] <= 150]

    all_suggestions = {}
    total_fields_with_suggestions = 0
    total_exercises_with_suggestions = 0

    for les in target_lessons:
        exs = get_lesson_exercises_data(les)
        for ex in exs:
            aid = ex['app_id']
            field_suggs = {}
            for field in ['tasktext', 'titel', 'untertitel', 'helptext', 'feedback']:
                val = ex.get(field) or ''
                if not val.strip():
                    continue

                sugg, reasons = proofread_text(val)
                if sugg != val and reasons:
                    diff_html = build_inline_diff_html(val, sugg)
                    field_suggs[field] = {
                        'field': field,
                        'original': val,
                        'suggested': sugg,
                        'diff_html': diff_html,
                        'reasons': reasons
                    }
                    total_fields_with_suggestions += 1

            if field_suggs:
                total_exercises_with_suggestions += 1
                all_suggestions[aid] = {
                    'app_id': aid,
                    'lesson': les,
                    'num_display': ex['num_display'],
                    'suggestions': field_suggs
                }

    print("Found %d exercises with suggestions (total %d fields with suggestions) in lessons 51..150" % (
        total_exercises_with_suggestions,
        total_fields_with_suggestions
    ))

    with open(SUGGESTIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_suggestions, f, ensure_ascii=False, indent=2)

    print("Saved suggestions database to %s" % SUGGESTIONS_PATH)


if __name__ == '__main__':
    main()
