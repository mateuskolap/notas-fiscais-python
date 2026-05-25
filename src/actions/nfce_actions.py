from bs4 import BeautifulSoup

from src.dtos.nfce_dtos import ParsedInvoice
from src.services.nfce.extractor import NfceExtractorFactory
from src.services.nfce.fetcher import NfcePageFetcher


class NfceActions:
    def __init__(
        self, fetcher: NfcePageFetcher, extractor_factory: NfceExtractorFactory
    ):
        self.fetcher = fetcher
        self.extractor_factory = extractor_factory

    async def parse(self, url: str) -> ParsedInvoice:
        html = await self.fetcher.fetch(url)
        soup = BeautifulSoup(html, 'lxml')
        extractor = self.extractor_factory.get_extractor(url)
        return extractor.extract(soup)
