from psycopg2 import connect
from psycopg2.extras import DictCursor


class DbConnection:
    """Класс для работы с соединением с базой данных."""

    def __init__(self, db_url: str):
        """Инициализирует DbConnection с URL базы данных.

        Args:
            db_url (str): Строка подключения к базе данных.
        """
        self.db_url = db_url

    def get_connection(self):
        """Получает соединение с базой данных.

        Returns:
            conn: Объект подключения к базе данных.
        """
        return connect(self.db_url)

    def commit(self, conn):
        """Коммитит изменения в базе данных."""
        conn.commit()

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        with conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def execute(self, query, params=None):
        conn = self.get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
