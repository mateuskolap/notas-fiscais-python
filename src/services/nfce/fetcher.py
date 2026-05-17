import httpx

from src.exceptions.base_exceptions import NfceScrapingException

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9',
}


class NfcePageFetcher:
    @staticmethod
    async def fetch(url: str) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, headers=_HEADERS)
                response.raise_for_status()
                return response.text
        except httpx.RequestError as exc:
            raise NfceScrapingException(f'Error connecting to SEFAZ: {exc}') from exc
        except httpx.HTTPStatusError as exc:
            raise NfceScrapingException(
                f'SEFAZ returned HTTP error: {exc.response.status_code}'
            ) from exc
