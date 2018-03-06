import os

from django.core.management import BaseCommand

from home.models import LessonPage, PageWithSidebar
from ._private import set_block


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('arg', type=str, nargs='+')
        parser.add_argument(
            '--put',
            action='store_true',
            dest='push',
            default=False,
            help='push html from file back to site',
        )
        parser.add_argument(
            '--get',
            action='store_true',
            dest='get',
            default=False,
            help='get html from page and store it in file'
        )
        parser.add_argument('--slug', action='store_true', dest='slug', default=False)

    def handle(self, *args, **options):
        if options['slug']:
            for slug in options['arg']:
                if options['push']:
                    self.from_html_page(slug)
                elif options['get']:
                    self.to_html_page(slug)
        elif options['arg'][0] == 'all':
            if options['push']:
                self.from_html_all_lecons()
            elif options['get']:
                self.to_html_all_lecons()
        else:
            for num in options['arg']:
                if options['push']:
                    self.from_html_lecon(num)
                elif options['get']:
                    self.to_html_lecon(num)

    def from_html_page(self, slug):
        page = self.get_page_by_slug(slug)
        self.write_blocks_to_page(
            blocks=self.read_file('html_files\\' + page.slug + '.html'),
            page=page
        )

    def to_html_page(self, slug):
        page = self.get_page_by_slug(slug)
        html = self.read_page_body(page)
        self.write_to_file(page.slug, html)

    def to_html_all_lecons(self):
        for page in LessonPage.objects.all():
            html = self.read_page(page)
            self.write_to_file(self.sortable(page.slug), html)

    def from_html_all_lecons(self):
        file_names = os.listdir('html_files')
        for file_name in file_names:
            if file_name.split('-')[0] == 'lecon' and int(file_name.split('-')[1].split('.')[0]) < 134:
                slug = self.unsortable(file_name).rstrip('.html')
                self.write_blocks_to_page(
                    blocks=self.read_file('html_files\\' + file_name),
                    page=LessonPage.objects.get(slug=slug)
                )

    def from_html_lecon(self, num):
        page = self.get_page_by_number(num)
        self.write_blocks_to_page(
            blocks=self.read_file('html_files\\' + self.sortable(page.slug) + '.html'),
            page=page
        )

    def to_html_lecon(self, num):
        page = self.get_page_by_number(num)
        html = self.read_page(page)
        self.write_to_file(self.sortable(page.slug), html)

    def write_blocks_to_page(self, blocks, page):
        for block in blocks['comments_for_lesson']:
            if block['type'] == 'html':
                try:
                    new_block = page.comments_for_lesson.__getitem__(block['i'])
                except:
                    pass
                new_block.value = block['value']
                set_block(block['i'], new_block, page.comments_for_lesson)
        for block in blocks['body']:
            if block['type'] == 'html':
                new_block = page.body.__getitem__(block['i'])
                new_block.value = block['value']
                set_block(block['i'], new_block, page.body)
        page.save()

    def read_page_body(self, page):
        doc = '\n<!--TAB_BODY--><br><a name="tab_body"/><br>\n'
        for i in range(len(page.body.stream_data)):
            block = page.body.__getitem__(i)
            num = '0' + str(i) if i < 10 else str(i)
            if block.block_type == 'html':
                doc = doc + '\n<!--BLOCK_HTML_' + num + '-->\n' + block.value
            elif block.block_type == 'paragraph':
                doc = doc + '\n<!--BLOCK_PRGF_' + num + '-->\n'
            elif block.block_type == 'audio':
                doc = doc + '\n<!--BLOCK_AUDI_' + num + '-->\n'
            elif block.block_type == 'advertisement':
                doc = doc + '\n<!--BLOCK_SNPT_' + num + '-->\n'
        doc = doc + '\n<!--TAB_BODY_END--><br><a name="tab_body_end"/><br>\n'
        return doc

    def read_page_comments(self, page):
        doc = '\n<!--TAB_COMMENTS--><br><a name="tab_comments"/><br>\n'
        for i in range(len(page.comments_for_lesson.stream_data)):
            block = page.comments_for_lesson.__getitem__(i)
            num = '0' + str(i) if i < 10 else str(i)
            if block.block_type == 'html':
                doc = doc + '\n<!--BLOCK_HTML_' + num + '-->\n' + block.value
        doc = doc + '\n<!--TAB_COMMENTS_END--><br><a name="tab_comments_end"/><br>\n'
        return doc

    def read_page_dictionary(self, page):
        doc = '\n<!--TAB_DICTIONARY--><br><a name="tab_dictionary"/><br>\n'
        for i in range(len(page.dictionary.stream_data)):
            block = page.dictionary.__getitem__(i)
            num = '0' + str(i) if i < 10 else str(i)
            if block.block_type == 'html':
                doc = doc + '\n<!--BLOCK_HTML_' + num + '-->\n' + block.value
        doc = doc + '\n<!--TAB_DICTIONARY_END--><br><a name="tab_dictionary_end"/><br>\n'
        return doc

    def read_page(self, page):
        return self.read_page_comments(page) + self.read_page_body(page) + self.read_page_dictionary(page)

    def write_to_file(self, file_name, doc):
        file_path = 'html_files\\' + file_name + '.html'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(doc)

    def read_file(self, file_path):
        blocks = {'comments_for_lesson': [], 'body': []}
        value = 'null'
        type_block = 'null'
        i = -1
        with open(file_path, 'r', encoding='utf-8') as f:
            self.stdout.write(file_path)
            for line in f:
                if line == '\n':
                    pass
                elif line.find('<!--TAB_') != -1:
                    pos = line.find('<!--TAB_') + 8
                    if line[pos:pos + 4] == 'COMM':
                        type_tab = 'comments'
                    else:
                        type_tab = 'body'
                elif line.find('<!--BLOCK_') != -1:
                    try:
                        print(type_tab)
                    except:
                        type_tab = 'body'
                    if type_tab == 'comments' and i != -1:
                        blocks['comments_for_lesson'].append({'type': type_block, 'value': value, 'i': i})
                    elif i != -1:
                        blocks['body'].append({'type': type_block, 'value': value, 'i': i})
                    pos = line.find('<!--BLOCK_') + 10
                    if line[pos:pos + 4] == 'HTML':
                        type_block = 'html'
                    else:
                        type_block = 'audio'
                    i = int(line[pos + 5:pos + 7])
                    value = ''
                else:
                    value = value + line
            if type_tab == 'comments':
                blocks['comments_for_lesson'].append({'type': type_block, 'value': value, 'i': i})
            else:
                blocks['body'].append({'type': type_block, 'value': value, 'i': i})
        return blocks

    def get_page_by_number(self, num):
        return LessonPage.objects.get(lesson_number=num)

    def get_page_by_slug(self, slug):
        try:
            return LessonPage.objects.get(slug=slug)
        except:
            return PageWithSidebar.objects.get(slug=slug)

    def sortable(self, file_name: str):
        self.stdout.write(file_name)
        return 'lecon-' + '{0:03}'.format(int(file_name.split('-')[1].rstrip('.html')))

    def unsortable(self, sortable_file_name: str):
        return 'lecon-' + str(int(sortable_file_name.split('-')[1].split('.')[0])) + '.html'