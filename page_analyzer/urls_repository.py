from psycopg2 import connect
from psycopg2.extras import DictCursor


class UrlsRepository:
    """Класс для работы с репозиторием URL."""

    def __init__(self, db_url):
        """Инициализирует UrlsRepository с URL базы данных.

        Args:
            db_url: Строка подключения к базе данных.
        """
        self.db_url = db_url

    def get_connection(self):
        """Получает соединение с базой данных.

        Returns:
            conn: Объект подключения к базе данных.
        """
        return connect(self.db_url)

    def get_all_urls(self):
        """Получает все URL и их последние проверки из базы данных.

        Returns:
            list: Список словарей, каждый из которых представляет
            строку из таблицы URLs и данные последних проверок,
            отсортированные по убыванию id.
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT urls.id, urls.name, urls.created_at,
                       url_checks.status_code AS response_code,
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
            """)
            rows = [dict(row) for row in cur]
        conn.close()
        return rows

    def find(self, id: int) -> dict | None:
        """Находит URL по идентификатору.

        Args:
            id (int): Идентификатор URL.

        Returns:
            dict | None: Возвращает словарь с данными URL, если
            найдено, иначе возвращает None.
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_url_id(self, url):
        """Получает идентификатор URL по его имени.

        Args:
            url (dict): Словарь, содержащий идентификатор URL

        Returns:
            int | None: Возвращает идентификатор URL, если найден,
            иначе возвращает None.
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url['url'],))
            row = cur.fetchone()
        conn.close()
        return row['id'] if row else None

    def save(self, url: dict) -> int | None:
        """Сохраняет новый URL в базе данных.

        Args:
            url (dict): Словарь, содержащий URL.

        Returns:
            int | None: Возвращает идентификатор сохраненного URL,
            если успешное сохранение, иначе возвращает None.
        """
        conn = self.get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url['url'],))
            existing_name = cur.fetchone()

            if existing_name:
                return None

            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                (url['url'],)
            )
            url_id = cur.fetchone()[0]
            conn.commit()
        conn.close()
        return url_id

    def save_checks(self, id: int, check_result: dict) -> None:
        """Сохраняет результаты проверки для указанного URL.

        Args:
            id (int): Идентификатор URL.
            check_result (dict): Словарь с результатами проверки,
            включая статус-код и метаданные страницы.

        Returns:
            None: В случае ошибки происходит откат транзакции
            и функция возвращает None.
        """
        conn = self.get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO
                 url_checks (url_id, status_code, h1, title, description)
                   VALUES (%s, %s, %s, %s, %s)""",
                (id, check_result['status_code'],
                 check_result['h1'], check_result['title'],
                 check_result['description'])
            )
            conn.commit()
        conn.close()

    def get_checks_for_url(self, id: int) -> list | None:
        """Получает результаты проверок для указанного URL.

        Args:
            id (int): Идентификатор URL.

        Returns:
            list | None: Возвращает список словарей с результатами
            проверок для данного URL или None, если проверки не найдены.
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""SELECT
                                id,
                                status_code,
                                h1,
                                title,
                                description,
                                created_at
                            FROM url_checks
                            WHERE url_id = %s
                             ORDER BY id DESC""", (id,))
            rows = cur.fetchall()
        conn.close()
        return rows if rows else None
