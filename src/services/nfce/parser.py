from bs4 import BeautifulSoup


def parse_html(html: str):
    return BeautifulSoup(html, 'lxml')