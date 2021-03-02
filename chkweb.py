#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config

import fire

import settings
import checks
import dba

__version__ = "0.1.4"

OK = "[OK] \u001b[32m✓\u001b[0m"

ERROR = "[ERROR] \u001b[31m✖\u001b[0m"

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('chkweb')


def status():
    """Show statistics about the crawling process.
    """
    db = dba.connect()
    stats = dba.get_status(db)
    total_pages = stats['checked_pages'] + stats['pending_pages']
    print('--[Status]---------------------------')
    print(f"Total pages known in database: {total_pages}")
    print(" - Processed: {checked_pages}".format(**stats))
    print(" - Failed: {failed_pages}".format(**stats))
    print(" - Pending: {pending_pages}".format(**stats))
    if total_pages:
        checked_pages = stats['checked_pages']
        progress = round(checked_pages * 100 / total_pages, 2)
        print(f"Progress: {progress:.2f}%")
    print('-------------------------------------')


def _list(db=None):
    """Shows a list of all the url address in the database.
    """
    db = db or dba.connect()
    for row in dba.get_all_pages(db):
        print("{id_page:10} {url:70} {is_checked}".format(**row))


def dump(db=None):
    """Dunmp all the address in CVS format.
    """
    db = db or dba.connect()
    print("id_page;url;created_at;is_checked;num_errors")
    for row in dba.get_all_pages(db):
        print(*row, sep="|")


def errors(db=None):
    """List all the errors found in the crawl.
    """
    db = db or dba.connect()
    print("id_page|message")
    for row in dba.get_all_errors(db):
        print(*row, sep="|")


def start(base_url='http://localhost/'):
    """Create a new database and initialize the crawling process.
    """
    logger.info('Crawling starts at %s', base_url)
    db = dba.connect()
    dba.reset(db)
    assert not dba.exists_url(db, base_url)
    dba.add_url(db, base_url)
    assert dba.exists_url(db, base_url)
    advance(db)


def advance(db=None, limit=settings.ADVANCE_LIMIT):
    db = db or dba.connect()
    for (i, page) in enumerate(dba.pending_urls(db)):
        url = page['url']
        logger.info('Checking %s', url)
        print(f"- checking {url}", end=' ')
        list_of_errors, new_links = checks.check_page(url)
        print(ERROR if list_of_errors else OK)
        dba.mark_url_as_checked(db, url, list_of_errors)
        for new_url in new_links:
            dba.add_url(db, new_url)
            assert dba.exists_url(db, new_url)
        if limit > 0 and i > limit:
            break


def version():
    """Returns current version of the script.
    """
    return __version__


def main():
    fire.Fire({
        "version": version,
        "status": status,
        "start": start,
        "dump": dump,
        "list": _list,
        "errors": errors,
        "advance": advance,
    })


if __name__ == "__main__":
    main()
