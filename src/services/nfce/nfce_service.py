from src.services.nfce.extractor import (
    extract_items,
    extract_store,
    extract_total,
)
from src.services.nfce.fetcher import fetch_page
from src.services.nfce.parser import parse_html


async def parse_nfce(url: str):
    html = await fetch_page(url)

    soup = parse_html(html)

    return {
        'store': extract_store(soup),
        'items': extract_items(soup),
        'total': extract_total(soup),
    }