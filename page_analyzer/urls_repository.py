from psycopg2.extras import DictCursor


class UrlsRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls ORDER BY id DESC")
            return [dict(row) for row in cur]

    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_id_url(self, url):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url['url'],))
            row = cur.fetchone()
            return row['id'] if row else None

    def save(self, url):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                    (url['url'],)
                )
                url_id = cur.fetchone()[0]
                self.conn.commit()
                return url_id
        except Exception:
            self.conn.rollback()
            return None

    def save_checks(self, id, check_result):
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
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при сохранении проверок: {e}")
            return None

    def get_checks_for_url(self, id):
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
