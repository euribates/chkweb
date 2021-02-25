## ChkWeb

This is a very simple web crawler to check the public webpages
in a webserver.

to use, call the subcommand start with the URL to crawl:

    chkweb start http://localhost/

This will create a sqlite3 database ``pages.db`` whith the urls being
detected by the spyder. It also checks this first page and add all the locals
links to the database as pending url to be checked. Now you can run:

    chkweb advance

to continue the crawling process. This is goiny to take at most 10
pending url and repeat the process with each of then;


### Logs

A log file is stored in ``logs/chklog.log``. You can change the
log level either in the settings file or declaring a environment variable
named ``CHKWEB_LOG_LEVEL`` to the desired level. It is set to ``ERROR``
by default.

### TODO things

- add an option in the `advance` command to set the number of pages
  being analized in every call. Set to 0 to indicate continue until all the
  pages are analized.

- Add an option to select the name and path of the database file. Alos include
  in the `settings.py` file.

### DONE things

- logs stored in some other location [DONE 0.1.2]
- Subcommand list to list the URLs in the database [DONE 0.1.2]
- Subcommand init to delete the database and start a new crawl proces [DONE 0.1.2]
- subcommand run to get a URL form the pending list and check it [DONE 0.1.2]
