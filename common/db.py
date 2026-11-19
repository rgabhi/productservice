"""Small explicit SQL helpers. Each service passes its own database URL."""
import os
from contextlib import contextmanager
from pathlib import Path
import psycopg
from psycopg.rows import dict_row


def database_url(service):
    return os.getenv('DATABASE_URL', f'postgresql://{service}:{service}@localhost:55432/{service}')


@contextmanager
def transaction(url):
    # Commit on normal exit; rollback on exception. No transaction spans services.
    with psycopg.connect(url, row_factory=dict_row, connect_timeout=3) as conn:
        yield conn


def initialize(url, schema_file):
    with transaction(url) as conn:
        conn.execute(Path('common/schema.sql').read_text())
        conn.execute(Path(schema_file).read_text())
