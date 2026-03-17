from django.db import models
from django.utils.text import slugify
import cyrtranslit


def cyrillic_slugify(value):
    """Transliterate Cyrillic characters to Latin for slug"""
    if value:
        return slugify(cyrtranslit.to_latin(value, 'ru'))
    return None
