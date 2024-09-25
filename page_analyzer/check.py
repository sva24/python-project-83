import requests
from bs4 import BeautifulSoup
from .db import DbConnection
from .errors import PageCheckError


class UrlChecks:
    """Класс для работы с проверками URL."""

    def __init__(self, db_connection: DbConnection):
        """Инициализирует UrlChecksRepository с объектом DbConnection

        Args:
            db_connection (DbConnection): Объект соединения с базой данных.
        """
        self.db_connection = db_connection

    def save_checks(self, id: int, check_result: dict) -> None:
        """Сохраняет результаты проверки для указанного URL.

        Args:
            id (int): Идентификатор URL.
            check_result (dict): Словарь с результатами проверки.

        Returns:
            None: В случае ошибки происходит откат транзакции.
        """
        query = """
            INSERT INTO url_checks
             (url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db_connection.execute(query,
                                   (id,
                                    check_result['status_code'],
                                    check_result['h1'],
                                    check_result['title'],
                                    check_result['description']))

    def get_checks_for_url(self, id: int) -> list | None:
        """Получает результаты проверок для указанного URL.

        Args:
            id (int): Идентификатор URL.

        Returns:
            list | None: Возвращает список словарей с результатами
            проверок для данного URL или None, если проверки не найдены.
        """
        query = """
            SELECT
                id,
                status_code,
                h1,
                title,
                description,
                created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        rows = self.db_connection.fetch_all(query, (id,))
        return rows if rows else None

    def check_page(self, url) -> dict | None:
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
