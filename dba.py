#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sqlite3
import functools

logger = logging.getLogger(__name__)


def _create_schema(db_conn, schema_filename='database-schema.sql'):
    with open(schema_filename) as _f:
        db_conn.executescript(_f.read())


def _scalar(db, sql, *args, cast=lambda x: x):
    row = next(db.execute(sql, args))
    return cast(row[0])


def _row(db, sql, *args):
    return next(db.execute(sql, args))


def _rows(db, sql, *args):
    for row in db.execute(sql, args):
        yield row


# Start of Public functions. Use only the functions defined below


@functools.lru_cache
def connect(db_filename='pages.db'):
    logger.info('Conectando a la base de datos %s', db_filename)
    is_new = not os.path.exists(db_filename)
    conn = sqlite3.connect(
        db_filename,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
    conn.row_factory = sqlite3.Row
    if is_new:
        logger.info('- Primera conexión a la base de datos, crearé el squema')
        _create_schema(conn)
        logger.info('- Base de datos creada')
    logger.info('Establecida conexión con la base de datos')
    return conn


def reset(db):
    logger.info("Reset database. Tables page and error will be flush out")
    with db:
        db.execute('DELETE FROM error')
        db.execute('DELETE FROM page')
    logger.info("  - Reset done")


def total_checked_pages(db):
    sql = "SELECT count(*) FROM page WHERE is_checked = 1"
    return _scalar(db, sql)


def total_pending_pages(db):
    sql = "SELECT count(*) FROM page WHERE is_checked = 0"
    return _scalar(db, sql)


def total_failed_pages(db):
    sql = "SELECT count(*) FROM page WHERE is_checked=1 and num_errors > 0"
    return _scalar(db, sql)


def get_status(db):
    return {
        "checked_pages": total_checked_pages(db),
        "pending_pages": total_pending_pages(db),
        "failed_pages": total_failed_pages(db),
    }


def pending_urls(db):
    sql = "SELECT * FROM page WHERE is_checked = 0 ORDER BY id_page"
    yield from _rows(db, sql)


def get_all_pages(db):
    sql = "SELECT * FROM page ORDER BY id_page"
    yield from _rows(db, sql)


def get_all_errors(db):
    sql = """
        SELECT p.url, e.message
          FROM error e
          LEFT JOIN page p ON p.id_page = e.page_id
         ORDER BY e.page_id
         """
    yield from _rows(db, sql)


def exists_url(db, url):
    sql = "SELECT count(*) FROM  page WHERE url = ?"
    return _scalar(db, sql, url, cast=bool)


def add_url(db, url):
    if exists_url(db, url):
        return 0
    sql = "INSERT INTO page (url) VALUES (?)"
    with db:
        result = db.execute(sql, (url,))
        return result


def mark_url_as_checked(db, url, errors, headers):
    id_page = _scalar(db, "SELECT id_page FROM page WHERE url = ?", url)
    powered_by = headers.get('X-Powered-By')
    with db:
        sql = (
            "UPDATE page"
            "   SET is_checked = 1,"
            "       num_errors = ?,"
            "       powered_by = ?"
            " WHERE id_page = ?"
        )
        db.execute(sql, (len(errors), powered_by, id_page,))
        result = 1
        db.execute("DELETE FROM error WHERE page_id = ?", (id_page, ))
        for err in errors:
            sql = 'INSERT INTO error (page_id, message) VALUES (?, ?)'
            db.execute(sql, (id_page, err))
            result += 1
        return result
