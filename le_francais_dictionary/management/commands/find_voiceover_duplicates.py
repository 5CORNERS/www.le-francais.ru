from django.core.management import BaseCommand
from le_francais_dictionary.models import Word, WordTranslation


class Command(BaseCommand):
    def handle(self, *args, **options):
        result = []
        result_s = ''
        for word in Word.objects.all().order_by('cd_id'):
            row = {'word': word, 'word_occurrences':[], 'translation_occurrences': []}
            if word._polly_url:
                word_url = word._polly_url
                row['filename'] = word_url.split('/')[-1]
                if '_SYNTH' in word_url or '_synth' in word_url:
                    occurrences = Word.objects.filter(_polly_url=word_url).exclude(cd_id=word.cd_id)
                    if occurrences.count() > 0:
                        row['word_occurrences'] = occurrences

            translation = word.first_translation
            row['translation'] = translation
            row['translation_filename'] = ''
            if translation._polly_url:
                translation_url = translation._polly_url
                row['translation_filename'] = translation_url.split('/')[-1]
                if '_SYNTH' in translation_url or '_synth' in translation_url:
                    occurrences = WordTranslation.objects.filter(_polly_url=translation_url).exclude(id=translation.id)
                    if occurrences.count() > 0:
                        row['translation_occurrences'] = occurrences
            if row['word_occurrences'] and not row['translation_occurrences']:
                row['lang'] = 'F'
            elif not row['word_occurrences'] and row['translation_occurrences']:
                row['lang'] = 'R'
            else:
                row['lang'] = 'F/R'
            if row['word_occurrences'] or row['translation_occurrences']:
                result.append(row)
        result_s += 'IDX\tFILENAME_FR\tFILENAME_RU\t\LANG\n'
        for row in sorted(result, key=lambda x: x['word'].cd_id):
            result_s += f'{row["word"].cd_id}\t{row["filename"]}\t{row["translation_filename"]}\t{row["lang"]}\n'
        with open('voiceover_duplicates.tsv', 'w', encoding='utf-8') as f:
            f.write(result_s)
        print([row['word'].cd_id for row in result])