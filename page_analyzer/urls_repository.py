from psycopg2.extras import DictCursor


class UrlsRepository:
    """Класс для работы с репозиторием URL.

    Класс предоставляет методы для взаимодействия с
    базой данных, включая получение, сохранение и поиск URL,
    а также сохранение результатов проверок.

    Attributes:
        conn: Объект подключения к базе данных.
    """

    def __init__(self, conn):
        """Инициализирует UrlsRepository с подключением к базе данных.

        Args:
            conn: Объект подключения к базе данных.
        """
        self.conn = conn

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()

    def get_content(self):
        """Получает все URL из базы данных.

        Returns:
            list: Список словарей, каждый из которых представляет
            строку из таблицы URLs, отсортированные по убыванию id
        """

        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls ORDER BY id DESC")
            return [dict(row) for row in cur]

    def find(self, id: int) -> dict | None:
        """Находит URL по идентификатору.

        Args:
            id (int): Идентификатор URL.

        Returns:
            dict | None: Возвращает словарь с данными URL, если
            найдено, иначе возвращает None.
        """

        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_id_url(self, url):
        """Получает идентификатор URL по его имени.

        Args:
            url (dict): Словарь, содержащий ключ URL.

        Returns:
            int | None: Возвращает идентификатор URL, если найден,
            иначе возвращает None.
        """

        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url['url'],))
            row = cur.fetchone()
            return row['id'] if row else None

    def save(self, url: dict) -> int | None:
        """Сохраняет новый URL в базе данных.

        Args:
            url (dict): Словарь, содержащий URL.

        Returns:
            int | None: Возвращает идентификатор сохраненного URL,
            если успешное сохранение, иначе возвращает None.
        """
        with self.conn.cursor() as cur:

            cur.execute("SELECT id FROM urls WHERE name = %s", (url['url'],))
            existing_name = cur.fetchone()

            if existing_name:
                return None

            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                (url['url'],)
            )
            url_id = cur.fetchone()[0]
            self.conn.commit()
            return url_id

    def save_checks(self, id: int, check_result: dict) -> None:
        """Сохраняет результаты проверки для указанного URL.

        Args:
            id (int): Идентификатор URL.
            check_result (dict): Словарь с результатами проверки,
            включая статус-код и метаданные страницы.

        Returns:
            None: В случае ошибки происходит откат транзакции
            и функция возвращает None
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO
                     url_checks (url_id, status_code, h1, title, description)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (id, check_result['status_code'],
                     check_result['h1'], check_result['title'],
                     check_result['description'])
                )
                self.conn.commit()
        except Exception:
            return None

    def get_checks_for_url(self, id: int) -> list | None:
        """Получает результаты проверок для указанного URL.

        Args:
            id (int): Идентификатор URL.

        Returns:
            list | None: Возвращает список словарей с результатами
            проверок для данного URL или None, если проверки не найдены.
        """
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
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
            return rows if rows else None
