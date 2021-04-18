#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from html.parser import HTMLParser
from urllib.parse import urljoin
import logging
import itertools

import requests


logger = logging.getLogger(__name__)


def is_local_url(base_path, url):
    return url.startswith(base_path)


class LinkExtractor(HTMLParser):

    def __init__(self, base_path, *args, **kwargs):
        super(LinkExtractor, self).__init__(*args, **kwargs)
        self.base_path = base_path
        self.links = set()
        self.images = set()
        self.styles = set()
        self.scripts = set()

    def normalize_url(self, url):
        return urljoin(self.base_path, url)

    def all_references(self):
        return itertools.chain(
            self.styles,
            self.scripts,
            self.images,
        )

    def handle_starttag(self, tag, attrs):
        parameters = dict(attrs)
        if tag == 'a':
            if url := parameters.get('href'):
                url = self.normalize_url(url)
                if is_local_url(self.base_path, url):
                    self.links.add(url)
        elif tag == 'link':
            if url := parameters.get('href'):
                self.styles.add(self.normalize_url(url))
        elif tag == 'img':
            if url := parameters.get('src'):
                self.images.add(self.normalize_url(url))
        elif tag == 'script':
            if url := parameters.get('src'):
                self.scripts.add(self.normalize_url(url))


def check_url_exists(url):
    if url.startswith('data:image'):
        return True, 'Image embebed, needs no check'
    req = requests.head(url)
    if req.ok:
        return True, f"{url} got a OK response"
    else:
        return False, f"HEAD response to {url} failed"


def load_content_from_url(url):
    try:
        resp = requests.get(url)
        if resp.ok:
            return True, resp.text, resp.headers
        else:
            return False, f"{resp.status_code} {resp.reason} {url}", resp.headers
    except ConnectionError as err:
        return False, str(err), {}


def check_page(url):
    logger.info('Checking %s:', url)
    is_ok, text, headers = load_content_from_url(url)
    if not is_ok:
        return [text], [], headers
    parser = LinkExtractor(url)
    parser.feed(text)
    logger.info(' - Found %s Links (Anchors)', len(parser.links))
    errors = []
    for ref_url in parser.all_references():
        full_url = urljoin(url, ref_url)
        is_ok, message = check_url_exists(full_url)
        if not is_ok:
            logging.debug(message)
            errors.append(message)
        else:
            logging.info(message)
    return errors, [urljoin(url, _) for _ in parser.links], headers
