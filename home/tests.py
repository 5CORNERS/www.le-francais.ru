from django.test import TestCase
from home.models import PageWithSidebar, ArticlePage

class Page2ArticleTestCase(TestCase):
    def setUp(self):
        PageWithSidebar.objects.create(
            path='00010001',
            depth='2',
            slug='slug',
            url_path='home',
            title='title',
            seo_title='seo_title',
            show_in_menus=True,
            menu_title='menu_title',
            is_nav_root=False,
            is_selectable=True,
            reference_title='reference_title',
            subtitle='subtitle',
            live=True,
        )


import docx
from lxml import etree
from home.utils import docx_parse_document


class DocxParserTestCase(TestCase):
    def test_paragraph_styles_and_block_transitions(self):
        doc = docx.Document()
        doc.add_paragraph('Heading text', style='Heading 1')
        doc.add_paragraph('Quote 1', style='Quote')
        doc.add_paragraph('Quote 2', style='Quote')
        doc.add_paragraph('Normal paragraph')
        doc.add_paragraph('Callout 1', style='Intense Quote')
        doc.add_paragraph('Callout 2', style='Intense Quote')
        doc.add_paragraph('List item 1', style='List Paragraph')
        doc.add_paragraph('List item 2', style='List Paragraph')
        doc.add_paragraph('Final paragraph')

        html, lines_map = docx_parse_document(doc)
        self.assertIn('<h2>Heading text</h2>', html)
        self.assertIn('<blockquote class="font-italic pl-4"><p>Quote 1</p><p>Quote 2</p></blockquote>', html)
        self.assertIn('<p>Normal paragraph</p>', html)
        self.assertIn('<div class="bs-callout bs-callout-info bs-callout-transcript"><p>Callout 1</p><p>Callout 2</p></div>', html)
        self.assertIn('<ul><li>List item 1</li><li>List item 2</li></ul>', html)
        self.assertIn('<p>Final paragraph</p>', html)

    def test_goback_bookmark_does_not_leak_or_break_opened_tags(self):
        doc = docx.Document()
        p = doc.add_paragraph()
        run = p.add_run('Text with GoBack')

        b_start = etree.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkStart',
                                {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id': '0',
                                 '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name': '_GoBack'})
        b_end = etree.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkEnd',
                              {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id': '0'})
        p._p.insert(0, b_start)
        p._p.append(b_end)

        html, lines_map = docx_parse_document(doc)
        self.assertNotIn('_GoBack', html)
        self.assertNotIn('<span id="_GoBack">', html)

    def test_bookmark_with_name_creates_span(self):
        doc = docx.Document()
        p = doc.add_paragraph()
        run = p.add_run('Bookmarked text')

        b_start = etree.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkStart',
                                {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id': '1',
                                 '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name': 'my_anchor'})
        b_end = etree.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkEnd',
                              {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id': '1'})
        p._p.insert(0, b_start)
        p._p.append(b_end)

        html, lines_map = docx_parse_document(doc)
        self.assertIn('<span id="my_anchor">', html)
        self.assertIn('</span>', html)