from swisstext.cmd.scraping.data import Page
from swisstext.cmd.scraping.tools import BasicDecider


class Decider(BasicDecider):

    def should_page_be_crawled(self, page: Page) -> bool:
        """Returns true only if the page is new."""
        return page.is_new()

    def should_children_be_crawled(self, page: Page) -> bool:
        if super().should_children_be_crawled(page):
            # just don't try going further if no new sg is found
            return len(page.new_sg) > 2
