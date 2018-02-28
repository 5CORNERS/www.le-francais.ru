import re

from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('html_files\\' + 'lecon-001' + '.html', 'r', encoding='utf-8') as f:
            page_body = PageBody(f)
            print('done!')

def read_all_lecons():


class Block:
    def __init__(self, block_type: str, block_num: int, raw_text=None):
        self.type = block_type
        self.n = block_num
        if raw_text:
            self.html = re.sub('^<!--BLOCK_([A-Za-z]{4})_([0-9]{2})-->$', '', raw_text, flags=re.M)


class PageBody:
    def __init__(self, file):
        self.file_lines = list((file))
        self.blocks = []
        block_pos = []
        for line_num, line in enumerate(self.file_lines):
            match = re.match('<!--BLOCK_([A-Za-z]{4})_([0-9]{2})-->', line)
            if bool(match):
                block_pos.append((line_num, int(match.group(2)), match.group(1)))
        for block_start in block_pos:
            block_type = block_start[2]
            block_num = block_start[1]
            if block_type == 'HTML':
                line_num = block_start[0] + 1
                block_raw_text = ''
                match = False
                while not match:
                    block_raw_text += self.file_lines[line_num]
                    match = re.match('(<!--BLOCK_HTML_[0-9]{2}-->)|(<!--TAB_BODY_END-->)', self.file_lines[line_num])
                    line_num += 1
                block = Block(block_type, block_num, block_raw_text)
            else:
                block = Block(block_type, block_num)
            self.blocks.append(block)

    def add_snippets(self):
        for block in self.blocks:
            if block.type == 'HTML':
                html_text = block.html
                re.match('()()()')