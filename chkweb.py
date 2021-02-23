#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from html.parser import HTMLParser
from urllib.parse import urlparse

import os
import sqlite3
import logging

import click
import itertools
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(
    logging.FileHandler('chkweb.log', encoding='utf-8')
    )


def db_connect(db_filename='pages.db'):
    is_new = not os.path.exists(db_filename)
    conn = sqlite3.connect(db_filename)
    logger.info('Conectando a la base de datos %s', db_filename)
    if is_new:
        logger.info('- Primera conexión a la base de datos, crearé el squema')
        db_create_schema(conn)
        logger.info('- Base de datos creada')
    logger.info('Establecida conexión con la base de datos')
    return conn


def db_create_schema(db_conn, schema_filename='database-schema.sql'):
    with open(schema_filename) as _f:
        db_conn.executescript(_f.read())


def db_exist_url(db, url):
    sql = "SELECT count(*) FROM  page WHERE url = ?"
    cur = db.cursor()
    cur.execute(sql, (url,))
    result = cur.fetchone()
    return bool(result[0])


def add_url(db, url):
    if db_exist_url(db, url):
        return 0
    sql = "INSERT INTO page (url) VALUES (?)"
    cur = db.cursor()
    try:
        result = cur.execute(sql, (url,))
        db.commit()
        return result
    finally:
        cur.close()


def mark_url_as_checked(db, url, num_errors):
    sql = (
        "UPDATE page"
        "   SET is_checked = 1,"
        "       num_errors = ?"
        " WHERE url = ?"
    )
    cur = db.cursor()
    try:
        result = cur.execute(sql, (num_errors, url,))
        db.commit()
        return result
    finally:
        cur.close()



def is_local_url(url):
    if url.lower().startswith('http'):
        return False
    if url.lower().startswith('//'):
        return False
    return True


def join_with_base(base_path, url):
    if base_path.endswith('/'):
        base_path = base_path[:-1]
    if url.startswith('/'):
        url = url[1:]
        o = urlparse(base_path)
        base_path = f"{o.scheme}://{o.netloc}"
    result = '/'.join([base_path, url])
    return result


def check_url_status(full_url):
    req = requests.head(full_url)
    return req.ok


def check_url(base_path, url):
    if not is_local_url(url):
        return f"{url} [NON LOCAL -  SKIPPED]"
    full_url = join_with_base(base_path, url)
    status_ok = check_url_status(full_url)
    click.echo(f"  - {full_url} [{'OK' if status_ok else 'ERROR'}]")
    return status_ok


class LinkExtractor(HTMLParser):

    def __init__(self, *args, **kwargs):
        super(LinkExtractor, self).__init__(*args, **kwargs)
        self.links = set()
        self.images = set()
        self.styles = set()
        self.scripts = set()

    def all_links(self):
        return itertools.chain(
            self.styles,
            self.scripts,
            self.images,
            self.links,
        )


    def handle_starttag(self, tag, attrs):
        parameters = dict(attrs)
        if tag == 'a':
            if url := parameters.get('href'):
                self.links.add(url)
        elif tag == 'link':
            if url := parameters.get('href'):
                self.styles.add(url)
        elif tag == 'img':
            if url := parameters.get('src'):
                self.images.add(url)
        elif tag == 'script':
            if url := parameters.get('src'):
                self.scripts.add(url)


def check_page(base_path, url):
    parser = LinkExtractor()
    req = requests.get(url)
    parser.feed(req.text)
    click.echo(f'Links (Anchors) found ({len(parser.links)})')
    num_errors = 0
    for url in parser.all_links():
        num_errors += 0 if check_url(base_path, url) else 1
    return num_errors, parser.links


def db_pending_urls(db):
    cursor = db.cursor()
    cursor.execute("SELECT url FROM page WHERE is_checked = 0")
    for row in cursor.fetchall():
        yield row[0]


@click.command()
@click.option('--path', default='', help="Path inside the webserver")
@click.option('--port', default=80, help="Port of web server")
@click.argument('host', default='localhost')
def chkweb(host='localhost', port=80, path=''):
    base_path = f'http://{host}:{port}/'
    if path:
        base_path = join_with_base(base_path, path)
    db = db_connect()
    add_url(db, base_path)
    for url in db_pending_urls(db):
        click.echo(f'Start crawling on {base_path}')
        num_errors, new_links = check_page(base_path, url)
        mark_url_as_checked(db, url, num_errors)


if __name__ == "__main__":
    chkweb()
