# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.test import SimpleTestCase
from custom_user.exercise_proofreader import (
    proofread_text,
    build_inline_diff_html,
    fix_typography,
    fix_abbreviations_and_spacing,
    fix_grammar_and_punctuation
)


class ExerciseProofreaderTestCase(SimpleTestCase):

    def test_typography_quotes_and_dashes(self):
        text = 'Слово "voiture" - это машина.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, 'Слово «voiture» — это машина.')
        tags = [r['tag'] for r in reasons]
        self.assertIn('кавычки', tags)
        self.assertIn('тире', tags)

    def test_html_tag_protection(self):
        text = '<span class="text-warning"><i><b>"mot"</b></i></span> - это пример.'
        sugg, reasons = proofread_text(text)
        # Attribute 'class="text-warning"' must NOT be broken into 'class=«text-warning»'!
        self.assertTrue('class="text-warning"' in sugg)
        self.assertTrue('«mot»' in sugg)
        self.assertTrue(' — ' in sugg)

    def test_abbreviations_spacing(self):
        text = 'Смотрите т.е. здесь, а также т.д. и т.п.'
        sugg, reasons = proofread_text(text)
        self.assertIn('т. е.', sugg)
        self.assertIn('т. д.', sugg)
        self.assertIn('т. п.', sugg)

    def test_expand_abbreviations(self):
        text = 'Существительное в женск. роде и муж. роде.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, 'Существительное в женском роде и мужском роде.')

    def test_grammar_tak_zhe_and_kak_v_primere(self):
        text = 'Дополните фразу словами также как в примере.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, 'Дополните фразу словами, так же, как в примере.')
        tags = [r['tag'] for r in reasons]
        self.assertIn('так же, как', tags)
        self.assertIn('запятая', tags)

    def test_numeral_affixes(self):
        text = 'В 1-ый раз и во 2-ой раз.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, 'В 1-й раз и во 2-й раз.')

    def test_inline_diff_html(self):
        orig = 'Дополните также как в примере'
        sugg = 'Дополните, так же, как в примере'
        diff = build_inline_diff_html(orig, sugg)
        self.assertIn('<del class="diff-del">', diff)
        self.assertIn('<ins class="diff-ins">', diff)

    def test_dash_before_kak_v_primere_never_adds_comma(self):
        text = 'Напишите, в каком году они произошли — как в примере.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, text)
        self.assertEqual(len(reasons), 0)

    def test_hyphen_before_kak_v_primere_converts_to_dash_without_comma(self):
        text = 'Напишите, в каком году они произошли - как в примере.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, 'Напишите, в каком году они произошли — как в примере.')
        tags = [r['tag'] for r in reasons]
        self.assertEqual(tags, ['тире'])

    def test_capitalized_vy_preserved_after_punctuation(self):
        text = 'В некоторых — нет. Вы помните, что это исключение.'
        sugg, reasons = proofread_text(text)
        self.assertIn('Вы помните', sugg)
        self.assertNotIn('вы помните', sugg)

    def test_parenthesis_before_kak_v_primere(self):
        text = 'Дополните таблицу (невозвратный / возвратный) — как в примере.'
        sugg, reasons = proofread_text(text)
        self.assertEqual(sugg, text)
