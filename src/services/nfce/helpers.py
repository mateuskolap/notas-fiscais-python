import re
import unicodedata
from decimal import Decimal

from bs4 import NavigableString, Tag


def clean_text(
    value: Tag | NavigableString | None, remove_text: str = ''
) -> str | None:
    if not value:
        return None

    text = value.get_text(strip=True)

    if remove_text:
        text = text.replace(remove_text, '')

    return text.strip()


def parse_brazilian_decimal(value: str | None) -> Decimal:
    if not value:
        return Decimal('0.00')

    cleaned = re.sub(r'[^\d,.-]', '', value.strip())
    cleaned = cleaned.replace(',', '.')

    try:
        return Decimal(cleaned)
    except Exception:
        return Decimal('0.00')


def normalize(value: str | None) -> str:
    if not value:
        return ''
    value = value.lower()
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]', '', value)
