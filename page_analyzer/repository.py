import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor


@contextmanager
def make_pg_conn(autocommit=True):
    database_url = os.getenv('DATABASE_URL')
    with psycopg2.connect(database_url, cursor_factory=RealDictCursor) as conn:
        conn.autocommit = autocommit
        yield conn


class URLRepository:
    def __init__(self, connection):
        self.conn = connection

    def get_by_name(self, name):
        query = """
            SELECT
                id, name, created_at 
            FROM urls 
            WHERE
                name = %s
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (name,))
            return cur.fetchone()

    def get_by_id(self, id):
        query = """
            SELECT
                id, name, created_at 
            FROM urls
            WHERE
                id = %s
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

    def insert_url(self, name):
        query = '''
            INSERT INTO urls (name)
            VALUES (%s)
            RETURNING id
        '''
        with self.conn.cursor() as cur:
            cur.execute(query, (name,))
            return cur.fetchone()['id']

    def insert_url_check(self, url_id, data):
        query = '''
        INSERT INTO url_checks (url_id, status_code, h1, title, description)
        VALUES (%s, %s, %s, %s, %s)
        '''
        with self.conn.cursor() as cur:
            cur.execute(query, (
                url_id,
                data.get('status'),
                data.get('h1'),
                data.get('title'),
                data.get('description'),
            ))

    def get_url_checks(self, url_id):
        query = '''
        SELECT * FROM url_checks
        WHERE url_id = %s
        ORDER BY id DESC
        '''
        with self.conn.cursor() as cur:
            cur.execute(query, (url_id,))
            url_checks = cur.fetchall()

            for row in url_checks:
                row['h1'] = row['h1'] or ''
                row['title'] = row['title'] or ''
                row['description'] = row['description'] or ''

            return url_checks

    def get_urls_checks(self):
        query = '''
        SELECT DISTINCT ON (urls.id)
            urls.id AS id, 
            urls.name AS name,
            url_checks.created_at  AS created_at,
            url_checks.status_code AS status_code
        FROM urls
        LEFT JOIN url_checks ON 
            urls.id = url_checks.url_id
        ORDER BY id, created_at DESC;
        '''
        with self.conn.cursor() as cur:
            cur.execute(query)
            urls_checks = cur.fetchall()

            for row in urls_checks:
                row['created_at'] = row['created_at'] or ''
                row['status_code'] = row['status_code'] or ''

            return urls_checks
