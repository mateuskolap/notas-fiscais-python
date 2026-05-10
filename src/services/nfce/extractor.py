from src.services.nfce.helpers import clean_text, to_float


def extract_store(soup):
    return {
        'name': clean_text(
            soup.find(class_='txtTopo')
        )
    }


def extract_items(soup):
    items = []

    products = soup.find_all('tr')

    for product in products:

        name = product.find(class_='txtTit2')

        if not name:
            continue

        code = clean_text(
            product.find(class_='RCod'),
            '(Código:'
        )

        if code:
            code = code.replace(')', '').strip()

        quantity = clean_text(
            product.find(class_='Rqtd'),
            'Qtde.:'
        )

        unit = clean_text(
            product.find(class_='RUN'),
            'UN:'
        )

        unit_price = clean_text(
            product.find(class_='RvlUnit'),
            'Vl. Unit.:'
        )

        total_price = clean_text(
            product.find(class_='valor')
        )

        item = {
            'name': clean_text(name),
            'code': code,
            'quantity': to_float(quantity),
            'unit': unit,
            'unit_price': to_float(unit_price),
            'total_price': to_float(total_price),
        }

        items.append(item)

    return items


def extract_total(soup):
    total = clean_text(
        soup.find(class_='txtMax')
    )

    return to_float(total)