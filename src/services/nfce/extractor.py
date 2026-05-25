import re
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import override
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from src.dtos.nfce_dtos import ParsedEstablishment, ParsedInvoice, ParsedInvoiceItem
from src.exceptions.base_exceptions import NfceScrapingException
from src.services.nfce.helpers import clean_text, normalize, parse_brazilian_decimal


class BaseNfceExtractor(ABC):
    @abstractmethod
    def extract(self, soup: BeautifulSoup) -> ParsedInvoice:
        pass

    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        pass


class TemplateNfceExtractor(BaseNfceExtractor):
    @override
    def extract(self, soup: BeautifulSoup) -> ParsedInvoice:
        return ParsedInvoice(
            establishment=self._extract_establishment(soup),
            issued_at=self._extract_issued_at(soup),
            total_value=self._extract_total_value(soup),
            discount_value=self._extract_discount_value(soup),
            items=self._extract_items(soup),
        )

    @abstractmethod
    def _extract_establishment(self, soup: BeautifulSoup) -> ParsedEstablishment:
        pass

    @abstractmethod
    def _extract_issued_at(self, soup: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def _extract_total_value(self, soup: BeautifulSoup) -> Decimal:
        pass

    @abstractmethod
    def _extract_discount_value(self, soup: BeautifulSoup) -> Decimal:
        pass

    @abstractmethod
    def _extract_items(self, soup: BeautifulSoup) -> list[ParsedInvoiceItem]:
        pass


class PrNfceExtractor(TemplateNfceExtractor):
    @classmethod
    @override
    def can_handle(cls, url: str) -> bool:
        parsed_url = urlparse(url)
        host = parsed_url.hostname or ''
        return host == 'fazenda.pr.gov.br' or host.endswith('.fazenda.pr.gov.br')

    @override
    def _extract_establishment(self, soup: BeautifulSoup) -> ParsedEstablishment:
        name_node = soup.find(class_='txtTopo')
        if not name_node:
            raise NfceScrapingException('Establishment name not found.')
        name = clean_text(name_node) or 'Unknown'

        business_tin = ''
        address = ''
        center_texts = soup.find_all(class_='text', limit=5)
        for node in center_texts:
            text = clean_text(node) or ''
            if 'CNPJ' in text:
                match = re.search(r'CNPJ\s*:\s*(.*)', text)
                if match:
                    business_tin = re.sub(r'[^\d]', '', match.group(1))
            elif not business_tin:
                if not address and text and text != name:
                    address = re.sub(r'\s+', ' ', text).strip()
            elif business_tin and not address and text:
                address = re.sub(r'\s+', ' ', text).strip()

        if not address:
            nodes = soup.select('.txtCenter .text')
            for node in nodes:
                text = clean_text(node) or ''
                if 'CNPJ' not in text and text and text != name:
                    address = re.sub(r'\s+', ' ', text).strip()
                    break

        if not business_tin:
            raise NfceScrapingException('CNPJ not found in NFC-e.')

        return ParsedEstablishment(
            name=name,
            business_tin=business_tin,
            address=address,
        )

    @override
    def _extract_issued_at(self, soup: BeautifulSoup) -> datetime:
        infos = soup.select_one('#infos ul li')
        if not infos:
            raise NfceScrapingException('Emission date not found.')

        text = clean_text(infos) or ''
        match = re.search(r'Emissão:\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', text)
        if not match:
            raise NfceScrapingException('Emission date not found.')

        try:
            return datetime.strptime(match.group(1), '%d/%m/%Y %H:%M:%S')
        except ValueError:
            raise NfceScrapingException('Invalid emission date format.')

    @staticmethod
    def _extract_value_by_label(soup: BeautifulSoup, label_text: str) -> str | None:
        rows = soup.select('#totalNota #linhaTotal')
        for row in rows:
            label = clean_text(row.find('label')) or ''
            if label_text in label:
                return clean_text(row.find(class_='totalNumb'))
        return None

    @override
    def _extract_total_value(self, soup: BeautifulSoup) -> Decimal:
        val = self._extract_value_by_label(soup, 'Valor a pagar')
        if not val:
            raise NfceScrapingException('Total value not found.')
        return parse_brazilian_decimal(val)

    @override
    def _extract_discount_value(self, soup: BeautifulSoup) -> Decimal:
        val = self._extract_value_by_label(soup, 'Desconto')
        if not val:
            return Decimal('0.00')
        return parse_brazilian_decimal(val)

    @override
    def _extract_items(self, soup: BeautifulSoup) -> list[ParsedInvoiceItem]:
        items: list[ParsedInvoiceItem] = []

        for product in soup.select('#tabResult tr'):
            if product.find(class_='txtTit2'):
                items.append(self._extract_single_item(product))

        return items

    @staticmethod
    def _extract_single_item(product: Tag) -> ParsedInvoiceItem:
        description = clean_text(product.find(class_='txtTit2')) or 'Unknown'

        code_text = clean_text(product.find(class_='RCod')) or ''
        code_match = re.search(r'Código:\s*(\d+)', code_text)
        code = code_match.group(1) if code_match else None

        qty_text = clean_text(product.find(class_='Rqtd')) or ''
        qty_match = re.search(r'Qtde\.\s*:\s*([\d,.]+)', qty_text)
        quantity = parse_brazilian_decimal(qty_match.group(1) if qty_match else '0')

        unit_text = clean_text(product.find(class_='RUN')) or ''
        unit_match = re.search(r'UN:\s*(.+)', unit_text)
        unit = normalize(unit_match.group(1) if unit_match else '')

        unit_price_text = clean_text(product.find(class_='RvlUnit')) or ''
        unit_price_match = re.search(r'Vl\.\s*Unit\.\s*:\s*([\d,.]+)', unit_price_text)
        unit_price = parse_brazilian_decimal(
            unit_price_match.group(1) if unit_price_match else '0'
        )

        total_price_text = clean_text(product.find(class_='valor'))
        total_price = parse_brazilian_decimal(total_price_text)

        return ParsedInvoiceItem(
            description=description,
            code=code,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            total_price=total_price,
        )


class NfceExtractorFactory:
    def __init__(self, extractors: list[type[BaseNfceExtractor]] | None = None):
        if extractors is None:
            self._extractors = [PrNfceExtractor]
        else:
            self._extractors = extractors

    def get_extractor(self, url: str) -> BaseNfceExtractor:
        for extractor_cls in self._extractors:
            if extractor_cls.can_handle(url):
                return extractor_cls()

        raise NfceScrapingException(
            f'No NFC-e extractor found for the provided URL: {url}'
        )
