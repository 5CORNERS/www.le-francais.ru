# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import uuid
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.utils.text import slugify

from forum.models import ForumAttachment


MAX_IMAGE_DIMENSION = 1400  # Max width or height in pixels
TARGET_MAX_FILE_SIZE = 1024 * 1024  # 1 MB target ceiling
ALLOWED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP', 'GIF'}


def fix_exif_orientation(img):
    """
    Corrects image orientation based on EXIF tag 0x0112 (Orientation).
    Compatible with Pillow 5.x.
    """
    try:
        exif = img._getexif()
        if exif:
            orientation = exif.get(0x0112)
            if orientation == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                img = img.transpose(Image.ROTATE_180)
            elif orientation == 4:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
            elif orientation == 6:
                img = img.transpose(Image.ROTATE_270)
            elif orientation == 7:
                img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
            elif orientation == 8:
                img = img.transpose(Image.ROTATE_90)
    except Exception:
        pass
    return img


def has_transparency(img):
    """
    Returns True if an image has actual transparent pixels.
    """
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        try:
            rgba = img.convert('RGBA')
            alpha = rgba.split()[3]
            min_alpha = alpha.getextrema()[0]
            return min_alpha < 255
        except Exception:
            return True
    return False


def process_uploaded_image(file_obj, user):
    """
    Processes an uploaded image: auto-orients, downsizes to <= 1400px,
    compresses to under 1MB, and saves to ForumAttachment on S3.
    """
    original_filename = os.path.basename(file_obj.name)
    try:
        img = Image.open(file_obj)
    except Exception as e:
        raise ValueError('Не удалось прочитать файл изображения: {}'.format(e))

    raw_format = (img.format or '').upper()
    if raw_format not in ALLOWED_FORMATS:
        raise ValueError('Неподдерживаемый формат изображения ({})'.format(raw_format))

    # Fix orientation
    img = fix_exif_orientation(img)

    # Downscale if larger than MAX_IMAGE_DIMENSION
    w, h = img.size
    if w > MAX_IMAGE_DIMENSION or h > MAX_IMAGE_DIMENSION:
        if w >= h:
            new_w = MAX_IMAGE_DIMENSION
            new_h = int(round(h * (MAX_IMAGE_DIMENSION / float(w))))
        else:
            new_h = MAX_IMAGE_DIMENSION
            new_w = int(round(w * (MAX_IMAGE_DIMENSION / float(h))))
        img = img.resize((new_w, new_h), Image.ANTIALIAS)

    # Determine save format and compress
    out_format = raw_format
    out_ext = '.jpg'

    if raw_format in ('JPEG', 'JPG'):
        if img.mode != 'RGB':
            img = img.convert('RGB')
        out_format = 'JPEG'
        out_ext = '.jpg'
    elif raw_format == 'PNG':
        if has_transparency(img):
            out_format = 'PNG'
            out_ext = '.png'
        else:
            # Opaque PNG (e.g. huge smartphone camera screenshot) -> convert to JPEG
            if img.mode != 'RGB':
                img = img.convert('RGB')
            out_format = 'JPEG'
            out_ext = '.jpg'
    elif raw_format == 'WEBP':
        out_format = 'WEBP'
        out_ext = '.webp'
    elif raw_format == 'GIF':
        out_format = 'GIF'
        out_ext = '.gif'

    out_io = BytesIO()
    if out_format == 'JPEG':
        img.save(out_io, format='JPEG', quality=82, optimize=True, progressive=True)
    elif out_format == 'PNG':
        img.save(out_io, format='PNG', optimize=True)
    elif out_format == 'WEBP':
        img.save(out_io, format='WEBP', quality=82, method=6)
    elif out_format == 'GIF':
        img.save(out_io, format='GIF', optimize=True)

    out_bytes = out_io.getvalue()

    # If resulting size still exceeds 1MB, reduce further
    if len(out_bytes) > TARGET_MAX_FILE_SIZE and out_format == 'JPEG':
        out_io = BytesIO()
        cur_w, cur_h = img.size
        reduced_img = img.resize((int(cur_w * 0.8), int(cur_h * 0.8)), Image.ANTIALIAS)
        reduced_img.save(out_io, format='JPEG', quality=75, optimize=True, progressive=True)
        out_bytes = out_io.getvalue()
        img = reduced_img

    final_size = len(out_bytes)
    final_w, final_h = img.size

    # Prepare storage filename
    base_name, _ = os.path.splitext(original_filename)
    slug = slugify(base_name) or 'image'
    unique_suffix = uuid.uuid4().hex[:8]
    storage_name = '{}_{}{}'.format(slug[:35], unique_suffix, out_ext)

    attachment = ForumAttachment(
        user=user,
        filename=original_filename,
        file_size=final_size,
        width=final_w,
        height=final_h,
    )
    attachment.file.save(storage_name, ContentFile(out_bytes), save=True)
    return attachment


def link_attachments_to_post(post, body_text):
    """
    Searches body_text for attachment URLs or filenames and connects any unlinked
    ForumAttachment belonging to post.user to this post.
    """
    if not post or not post.pk or not body_text:
        return
    # Find any references to forum/images/ in the text
    matches = re.findall(r'forum/images/[\w/-]+\.[\w]+', body_text)
    if matches:
        for match in set(matches):
            ForumAttachment.objects.filter(
                user=post.user,
                post__isnull=True,
                file__icontains=match
            ).update(post=post)
