from Scrapper import WebScrapper
from YFinanceFinder import YFinanceFinder


def get_price_finder(web_scraper=False):

    if web_scraper:
        return WebScrapper()
    return YFinanceFinder()