from .models import Url
from .validator import UrlValidator, UrlNormalizer
from .db import DbConnection
from .errors import WrongUrl, UrlInDatabase


class UrlsRepository:
    """Класс для работы с репозиторием URL."""

    def __init__(self, db_connection: DbConnection,
                 url_validator: UrlValidator,
                 url_normalizer: UrlNormalizer):
        """Инициализирует UrlsRepository с объектом DbConnection
         валидатором и нормализатором.

        Args:
            db_connection (DbConnection): Объект соединения с базой данных.
            url_validator (UrlValidator): Объект для валидации URL.
            url_normalizer (UrlNormalizer): Объект для нормализации URL.
        """
        self.db_connection = db_connection
        self.url_validator = url_validator
        self.url_normalizer = url_normalizer

    def get_all_urls(self) -> list[Url]:
        """Получает все URL и их последние проверки из базы данных.

        Returns:
            list[Url]: Список объектов Url с данными из базы.
        """
        query = """
            SELECT urls.id, urls.name, urls.created_at,
                   url_checks.status_code,
                   url_checks.created_at AS last_checked
            FROM urls
            LEFT JOIN url_checks
            ON urls.id = url_checks.url_id
            AND url_checks.created_at = (
                SELECT MAX(created_at)
                FROM url_checks
                WHERE url_checks.url_id = urls.id
            )
            ORDER BY urls.id DESC
        """
        rows = self.db_connection.fetch_all(query)
        return [Url(**row) for row in rows]

    def find(self, id: int) -> Url | None:
        """Находит URL по идентификатору.

        Args:
            id (int): Идентификатор URL.

        Returns:
            Url | None: Возвращает объект Url, если найдено,
             иначе возвращает None.
        """
        query = "SELECT * FROM urls WHERE id = %s"
        rows = self.db_connection.fetch_all(query, (id,))
        return Url(**rows[0]) if rows else None

    def get_url_id(self, url: str) -> int | None:
        """Получает идентификатор URL по его имени.

        Args:
            url (str): Имя URL.

        Returns:
            int | None: Возвращает идентификатор URL, если найден,
             иначе возвращает None.
        """
        url_normalizer = self.url_normalizer.set_url(url)
        normalized_url = url_normalizer.normalize()
        query = "SELECT id FROM urls WHERE name = %s"
        rows = self.db_connection.fetch_all(query, (normalized_url,))
        return rows[0]['id'] if rows else None

    def save(self, url: Url) -> int:
        """Сохраняет новый URL в базе данных.

        Args:
            url (Url): Объект Url.

        Returns:
            int: Возвращает идентификатор сохраненного URL.

        Raises:
            WrongUrl: Если URL некорректен.
            UrlInDatabase: Если URL уже существует в базе данных.
        """

        url_validator = self.url_validator.set_url(url.name)

        errors = url_validator.validate().get_errors()
        if errors:
            raise WrongUrl(errors)

        url_normalizer = self.url_normalizer.set_url(url.name)
        normalized_url = url_normalizer.normalize()

        existing_name = self.get_url_id(normalized_url)
        if existing_name:
            raise UrlInDatabase("Страница уже существует")

        query = "INSERT INTO urls (name) VALUES (%s) RETURNING id"

        rows = self.db_connection.fetch_all(query, (normalized_url,))

        if rows:
            return rows[0]['id']
