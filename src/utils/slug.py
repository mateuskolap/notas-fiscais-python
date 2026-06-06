import re

from unidecode import unidecode


def generate_slug(name: str) -> str:
    slug = unidecode(name).lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug
