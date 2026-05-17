from bs4 import BeautifulSoup

from src.dtos.nfce_dtos import ParsedInvoice
from src.services.nfce.extractor import NfceDataExtractor
from src.services.nfce.fetcher import NfcePageFetcher


class NfceActions:
    def __init__(self, fetcher: NfcePageFetcher, extractor: NfceDataExtractor):
        self.fetcher = fetcher
        self.extractor = extractor

    async def parse(self, url: str) -> ParsedInvoice:
        html = await self.fetcher.fetch(url)
        soup = BeautifulSoup(html, 'lxml')
        return self.extractor.extract(soup)
