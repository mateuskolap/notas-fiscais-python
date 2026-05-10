def clean_text(value, remove_text: str = ''):
    if not value:
        return None

    text = value.get_text(strip=True)

    if remove_text:
        text = text.replace(remove_text, '')

    return text.strip()


def to_float(value: str | None):
    if not value:
        return None

    value = value.replace('.', '')
    value = value.replace(',', '.')

    try:
        return float(value)
    except ValueError:
        return None