from wagtail.core import blocks

class ChoosenReviews(blocks.StructBlock):
    class Meta:
        template = 'blocks/choosen_reviews.html'
        icon = 'openquote'