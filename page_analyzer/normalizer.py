from urllib.parse import urlparse


def normalize(url: str) -> str:
    """Нормализует URL, преобразуя его в нижний регистр.

    Args:
        url (str): Не нормализованный URL-адрес.

    Returns:
        str: Нормализованный URL в формате 'scheme://netloc',
        где 'scheme' и 'netloc' приведены к нижнему регистру.
    """
    parsed_url = {}
    url = urlparse(url['url'])
    parsed_url['url'] = f'{url.scheme.lower()}://{url.netloc.lower()}'
    return parsed_url
