"""
This UrlFilter is especially made for Swiss German. It fixes some of the problems we discovered while running
tests and gathering the SwissCrawl corpus.
"""

from typing import Optional

from swisstext.cmd.scraping.interfaces import IUrlFilter
import re


class SgUrlFilter(IUrlFilter):
    EXCLUDED_DOMAINS = {
        # pdfs
        'epdf.pub',
        'archive.org',
        'www.researchgate.net',

        # cgi interface of dictionary / book
        'woerterbuchnetz.de',
        'reichstagsakten.de',  # old deutsch
        'www.dididoktor.de',  # old deutsch
        'www.dwds.de',
        'ahdw.saw-leipzig.de',
        'awb.saw-leipzig.de',
        'mvdok.lbmv.de',  # scans of old German books / affidavits
        'www.lindehe.de',
        'wwwmayr.in.tum.de',
        # https://wwwmayr.in.tum.de/spp1307/patterns/patterns_text-german_1024_edit_32.txt German .txt with strange encoding

        # misc
        'neon.niederlandistik.fu-berlin.de',  # netherlands

        # songs
        # 'www.karaoke-lyrics.net',
        # 'www.musixmatch.com',
        # 'greatsong.net',

        # schwäbisch
        'www.schoofseggl.de',
        'www.schwaebisch-englisch.de',
        'www.theater-in-bach.de',

        # other
        'yigg.de',  # redirects
    }

    def fix(self, url: str) -> Optional[str]:
        if '://www.schnupfspruch.ch/' in url:
            # remove the parameter saying from which page we got there
            return re.sub('[&?]PrevPage=[\d]+', '', url)
        if '://www.literaturland.ch' in url:
            # all links are actually pointing to the same text...
            return 'http://www.literaturland.ch'
        if '://www.babyforum.ch/discussion/comment' in url:
            # all comments are actually behaving like anchors in the page
            # see for example https://www.babyforum.ch/discussion/3605/swissmom-party-2/p2
            # (comment links are on the dates on the upper right of posts)
            return None
        if '://www.fcbforum.ch' in url:
            if re.search('[&?]p=', url) is not None:
                # we only want to crawl "main pages", e.g. page link or subforum link
                # the p= parameter is added when clicking on a post link
                return None
            # remove the viewfull
            return re.sub('[&?]viewfull=1', '', url)

        elif any(f'://{excl}' in url for excl in self.EXCLUDED_DOMAINS):
            return None

        return url