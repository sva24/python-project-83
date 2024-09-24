import requests
from bs4 import BeautifulSoup


class PageCheckError(Exception):
    """Исключение для ошибок проверки страницы."""
    pass


def check_page(url) -> dict | None:
    """Проверяет доступность веб-страницы и извлекает метаданные.

    Args:
        url (str): URL-адрес веб-страницы для проверки.

    Returns:
        dict или None: Возвращает словарь с метаданными страницы,
        включая статус-код, заголовок H1, заголовок страницы и
        мета-описание, если запрос успешен. Если запрос неуспешен,
        возвращает None.
    """
    session = requests.Session()
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.HTTPError:
        raise PageCheckError('Произошла ошибка при проверке')
    except requests.ConnectionError:
        raise PageCheckError('Произошла ошибка при проверке')

    soup = BeautifulSoup(response.content, 'html.parser')
    h1 = soup.find('h1').text if soup.find('h1') else ''
    title = soup.title.string if soup.title.string else ''
    descrip_tag = soup.find('meta', {'name': 'description'})
    description = descrip_tag.get('content') if descrip_tag else None
    url_check = {
        'status_code': response.status_code,
        'h1': h1,
        'title': title,
        'description': description
    }
    return url_check
