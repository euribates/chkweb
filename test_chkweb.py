#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile

import pytest

import chkweb


def test_is_local_url():
    assert chkweb.is_local_url('/index.py') is True
    assert chkweb.is_local_url('http://www.python.org/') is False
    assert chkweb.is_local_url('https://www.python.org/') is False
    assert chkweb.is_local_url('//www.python.org/') is False


def tests_join_with_base():
    join_with_base = chkweb.join_with_base
    expected = "http://www.python.org/downloads/"
    assert join_with_base("http://www.python.org/", "/downloads/") == expected
    assert join_with_base("http://www.python.org", "/downloads/") == expected
    assert join_with_base("http://www.python.org/", "downloads/") == expected
    assert join_with_base("http://www.python.org", "downloads/") == expected


def tests_join_with_base_with_path_non_empty():
    join_with_base = chkweb.join_with_base
    expected = "http://www.python.org/downloads/"
    base = "http://www.python.org/community/"
    assert join_with_base(base, "/downloads/") == expected


# Database


def test_database_creation_and_connection():
    db = chkweb.db_connect(":memory:")
    cur = db.cursor()
    cur.execute("INSERT INTO page (url) VALUES ('http://www.parcan.es/')")
    cur.execute("SELECT id_page, url, is_checked FROM page")
    id_page, url, is_checked = cur.fetchone()
    assert id_page == 1
    assert url == 'http://www.parcan.es/'
    assert not is_checked


if __name__ == "__main__":
    pytest.main()
