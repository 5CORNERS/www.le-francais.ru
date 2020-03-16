from wagtail.core.models import Page
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.blocks.stream_block import StreamValue


def import_table(fp, split_by='	'):
    d = {}
    with open(fp, 'r', encoding='utf-8-sig') as f:
        for line in f:
            key, val = line.rstrip('\n').split(split_by)
            d[key] = val
        return d


def create_redirect(url_out, to, is_permanent=True):
    if isinstance(to, str):
        new_redirect, created = Redirect.objects.get_or_create(
            old_path=url_out,
            redirect_link=to,
        )
    elif isinstance(to, int):
        new_redirect, created = Redirect.objects.get_or_create(
            old_path=url_out,
            redirect_page_id=to,
        )
    else:
        return None
    if is_permanent:
        new_redirect.permanent = True
    return new_redirect


def set_block(i, new_block, stream_value):
    if isinstance(new_block, stream_value.StreamChild):
        if stream_value.is_lazy:
            data_item = {'type': new_block.block_type, 'value': new_block.value}
        else:
            data_item = (new_block.block_type, new_block.value)
        stream_value.stream_data[i] = data_item
        stream_value._bound_blocks[i] = new_block
        return

def del_block(i, stream_value):
    stream_value.stream_data.pop(i)
    # stream_value._bound_blocks.pop(i)

def merge_blocks(i1, i2, stream_value):
    block1 = stream_value.__getitem__(i1)
    block2 = stream_value.__getitem__(i2)
    new_value = block1.value + block2.value
    block1.value = new_value
    set_block(i1, block1, stream_value)
    del_block(i2, stream_value)
    return stream_value

import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
