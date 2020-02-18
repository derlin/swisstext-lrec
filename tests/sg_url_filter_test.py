import pytest
from swisstext.cmd import link_utils
from lrec_tools.sg_url_filter import SgUrlFilter


@pytest.fixture
def sg_filter():
    return SgUrlFilter()


test_cases = [
    (
        "http://www.schnupfspruch.ch/sprueche_view.asp?MOVE=84&PrevPage=33",
        "http://www.schnupfspruch.ch/sprueche_view.asp?MOVE=84"),
    (
        "http://www.literaturland.ch/appenzeller-anthologie/das-buch/",
        "http://www.literaturland.ch"),
    (
        "http://skyandsea.blog/2018/07/17/traumstraende-die-schoensten-straende-von-portugal-und-galizien-grossartige-instagram-foto-strand-motive/?replytocom=193",
        "http://skyandsea.blog/2018/07/17/traumstraende-die-schoensten-straende-von-portugal-und-galizien-grossartige-instagram-foto-strand-motive/"),
    (
        "https://www.babyforum.ch/discussion/3559/ich-bin-huet-rauchfrei",
        "https://www.babyforum.ch/discussion/3559/ich-bin-huet-rauchfrei"),
    (
        "https://www.babyforum.ch/discussion/comment/28015/",
        None),
    (
        "http://www.fcbforum.ch/forum/showthread.php?9533-News-und-Transfers-Fussball",
        "http://www.fcbforum.ch/forum/showthread.php?9533-News-und-Transfers-Fussball"),
    # (
    #     "http://www.fcbforum.ch/forum/showthread.php?p=1701381#post1701381",
    #     None),
    (
        "http://www.fcbforum.ch/forum/showthread.php?9533-News-und-Transfers-Fussball/page11",
        "http://www.fcbforum.ch/forum/showthread.php?9533-News-und-Transfers-Fussball/page11"),
    (
        "http://www.fcbforum.ch/forum/showthread.php?s=3a4a96e31e37ae9ece97d59866386fa2&p=1062865",
        None),
    (
        "http://www.fcbforum.ch/forum/showthread.php?30899-Cablecom-so-eine-scheisse&s=3a4a96e31e37ae9ece97d59866386fa2&p=1062920&viewfull=1",
        None),
    (
        "http://yigg.de/neu?exturl=http%3A%2F%2Fwww.fcbforum.ch%2Fforum%2Fshowthread.php%3Ft%3D1873&title=Chiumiento+und+Behrami+im+Nati-Aufgebot",
        None),
    (
        "http://woerterbuchnetz.de/cgi-bin/WBNetz/call_wbgui_py_from_form?sigle=DWB&mode=Volltextsuche&hitlist=&patternlist=&lemid=GN01312",
        None),
    (
        "http://www.zeno.org/Wander-1867/A/Metzger",
        "http://www.zeno.org/Wander-1867/A/Metzger"),
    (
        "http://web.archive.org/web/20010302135845/http://www.stillerhas.ch/texte/aare.html",
        "http://web.archive.org/web/20010302135845/http://www.stillerhas.ch/texte/aare.html"),
    (
        "http://archive.org/web/20010302135845/http://www.stillerhas.ch/texte/aare.html",
        None)
]


@pytest.mark.parametrize(
    "raw,expected",
    test_cases
)
def test_normalizer_single(sg_filter, raw, expected):
    fixed, ok = link_utils.fix_url(raw)
    assert ok
    result = sg_filter.fix(fixed)
    assert result == expected
