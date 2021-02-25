#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

import checks

HTML_SAMPLE = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width" />
    <title>Demo</title>
    <link rel="styleshet" href="/local/stylesheet.css">
  </head>
  <body>
    <img src="http://www.parcan.es/static/art/escudo.png">
    <ul>
      <li><a href="/about/">About</a></li>
      <li><a href="http://localhost/help/">Stack Overflow</a></li>
      <li><a href="http://www.wikipedia.com">Wikipedia</a></li>
    </ul>
    <script src="/static/js/custom.js">
  </body>
</html>"""


@pytest.fixture
def extractor():
    ext = checks.LinkExtractor('http://localhost/')
    ext.feed(HTML_SAMPLE)
    return ext


def test_extractor_links(extractor):
    expected = set([
        "http://localhost/about/",
        "http://localhost/help/",
    ])
    assert extractor.links == expected


def test_extractor_styles(extractor):
    expected = set([
        "http://localhost/local/stylesheet.css",
    ])
    assert extractor.styles == expected


def test_extractor_images(extractor):
    expected = set([
        "http://www.parcan.es/static/art/escudo.png",
    ])
    assert extractor.images == expected


def test_extractor_script(extractor):
    assert extractor.scripts == set([
        "http://localhost/static/js/custom.js"
    ])


# Testing check_url


# Testing is_local_url function


def test_is_local_url_true_case():
    base = 'http://localhost/'
    url = 'http://localhost/index.py'
    assert checks.is_local_url(base, url) is True


def test_is_local_url_false_case():
    base = 'http://localhost/'
    url = 'http://www.google.com/help/'
    assert checks.is_local_url(base, url) is False


if __name__ == "__main__":
    pytest.main()
