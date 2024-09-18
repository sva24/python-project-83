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
