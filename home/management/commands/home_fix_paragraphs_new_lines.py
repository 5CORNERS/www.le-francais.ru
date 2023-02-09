import json

from django.core.management import BaseCommand
from wagtail.core.models import PageRevision

from home.models import LessonPage
from ._private import set_block

class Command(BaseCommand):
    def handle(self, *args, **options):
        for l in LessonPage.objects.all():
            l_changed = False
            for i, b in enumerate(l.body):
                if b.block_type == 'paragraph' and '\n' in b.value.source and not '\r' in b.value.source:
                    l_changed = True
                    b.value.source = b.value.source.replace('\n', '<br>').replace('<br>-', '<br>\u2014')
                    if b.value.source[0] == '-':
                        b.value.source = '\u2014' + b.value.source[1:]
                    elif b.value.source[0:2] == '﻿-':
                        b.value.source = '﻿\u2014' + b.value.source[2:]
                    set_block(i, b, l.body)
                elif b.block_type == 'paragraph' and '<br>' in b.value.source:
                    l_changed = True
                    b.value.source = b.value.source.replace('<br>', '<br/>')
                    if b.value.source[0] == '-':
                        b.value.source = '\u2014' + b.value.source[1:]
                    elif b.value.source[0:2] == '﻿-':
                        b.value.source = '﻿\u2014' + b.value.source[2:]
                    elif b.value.source[0:5] == '<p>﻿-':
                        b.value.source = '<p>﻿\u2014' + b.value.source[5:]
                    set_block(i, b, l.body)
            if l_changed:
                print(l.lesson_number)
                l.save(update_fields=['body'])
            for r in l.revisions.all():
                r:PageRevision
                r_content_decoded = json.loads(r.content_json)
                r_body = json.loads(r_content_decoded["body"])
                new_r_body = []
                changed = False
                for r_body_block in r_body:
                    if r_body_block['type'] == 'paragraph' and '\n' in r_body_block['value'] and not '\r' in r_body_block['value']:
                        r_body_block['value'] = r_body_block['value'].replace('\n', '<br>').replace('<br>-', '<br>\u2014')
                        if r_body_block['value'][0] == '-':
                            r_body_block['value'] = '\u2014' + r_body_block['value'][1:]
                        elif r_body_block['value'][0:2] == '﻿-':
                            r_body_block['value'] = '﻿\u2014' + r_body_block['value'][2:]
                        changed = True
                    elif r_body_block['type'] == 'paragraph' and '<br>' in r_body_block['value']:
                        r_body_block['value'] = r_body_block['value'].replace('<br>', '<br/>')
                        if r_body_block['value'][0] == '-':
                            r_body_block['value'] = '\u2014' + r_body_block['value'][1:]
                        elif r_body_block['value'][0:2] == '﻿-':
                            r_body_block['value'] = '﻿\u2014' + r_body_block['value'][2:]
                        elif r_body_block['value'][0:5] == '<p>﻿-':
                            r_body_block['value'] = '<p>﻿\u2014' + r_body_block['value'][5:]
                        changed = True
                    new_r_body.append(r_body_block)
                r_content_decoded["body"] = json.dumps(new_r_body)
                r.content_json = json.dumps(r_content_decoded)
                if changed:
                    print(r)
                    r.save(update_fields=['content_json'])
