"""
A script that adds a list of URLs to MongoDB.

Usually, you would run this script with a list of URLs, then launch st_scrape in mongo mode (i.e. the URLs should
be pulled from mongo). Example:
```bash
st_scrape from_mongo --what new --how oldest
```

Doing it in this order instead of using `st_scrape from_file` is useful when you have a lot of URLs and want to
run the crawler in small batches. Instead of trying to segment your URL text file by hand, you can simply specify
how many new URLs to crawl using st_scrape's `-n` option.
"""

import argparse
import sys

from swisstext.mongo.models import MongoURL, Source, SourceType, get_connection
from swisstext.cmd.link_utils import fix_url
from urllib.parse import urlparse
import logging


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url_file', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-s', '--source_info', type=str, default=None)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=27017)
    parser.add_argument('--db', type=str, default='swisstext')
    parser.add_argument('-d', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stderr,
        format="[%(levelname)-5s] %(message)s",
        level=logging.DEBUG if args.d else logging.INFO)

    get_connection(db=args.db, host=args.mongo_host, port=args.port)

    enqueued, malformed, ignored, dup = 0, 0, 0, 0
    for i, line in enumerate(args.url_file):
        raw_url = line.strip()
        if len(raw_url) == 0 or raw_url.isspace():
            continue

        if not is_url(raw_url):
            malformed += 1
            logging.error(f'malformed url: {raw_url}')
            continue

        url, interesting = fix_url(raw_url)
        if not interesting:
            ignored += 1
            logging.warning(f'Uninteresting url: {url}')

        elif MongoURL.exists(url):
            dup += 1
            logging.debug(f'Duplicate url {url}. Skipping.')

        else:
            MongoURL.create(url, Source(SourceType.UNKNOWN, args.source_info)).save()
            enqueued += 1
            logging.debug(f'enqueued {url}')

    print(f'Enqueued URLs: {enqueued}/{i + 1} ({malformed} malformed) ({ignored} ignored) ({dup} duplicates).')


if __name__ == '__main__':
    main()
