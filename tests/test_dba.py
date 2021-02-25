#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

import dba


def test_database_creation_and_connection():
    dba.connect(":memory:")


def test_database_insert_page():
    conn = dba.connect(":memory:")
    conn.execute("INSERT INTO page (url) VALUES ('http://www.parcan.es/')")
    row = next(conn.execute(
        "SELECT id_page, url, is_checked, num_errors FROM page"
    ))
    assert row['id_page'] == 1
    assert row['url'] == 'http://www.parcan.es/'
    assert row['is_checked'] == 0
    assert row['num_errors'] == 0


@pytest.fixture
def fake_db():
    db = dba.connect(":memory:")
    dba.reset(db)
    db.execute("INSERT INTO page (url) VALUES ('http://www.github.com/')")
    db.execute("INSERT INTO page (url) VALUES ('http://www.parcan.es/')")
    db.execute("INSERT INTO page (url) VALUES ('http://www.google.com/')")
    yield db
    dba.reset(db)


def test_add_url(fake_db):
    url = 'http://sqlite.org/'
    assert dba.exists_url(fake_db, url) is False
    dba.add_url(fake_db, url)
    assert dba.exists_url(fake_db, url) is True


def test_exists_url(fake_db):
    assert dba.exists_url(fake_db, 'http://www.google.com/') is True
    assert dba.exists_url(fake_db, 'http://www.twitter.com/') is False


def test_total_checked_pages(fake_db):
    assert dba.total_checked_pages(fake_db) == 0
    fake_db.execute('UPDATE page set is_checked=1 WHERE id_page=1')
    assert dba.total_checked_pages(fake_db) == 1


def test_total_pending_pages(fake_db):
    assert dba.total_pending_pages(fake_db) == 3
    fake_db.execute('UPDATE page set is_checked=1 WHERE id_page=1')
    assert dba.total_pending_pages(fake_db) == 2


def test_total_failed_pages(fake_db):
    assert dba.total_failed_pages(fake_db) == 0
    fake_db.execute(
        'UPDATE page set is_checked=1, num_errors=23 WHERE id_page=1'
        )
    assert dba.total_failed_pages(fake_db) == 1


if __name__ == "__main__":
    pytest.main()
