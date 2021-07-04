import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from datetime import datetime
from StockPriceFinder import StockPriceFinder


class WebScrapper(StockPriceFinder):

    NUM_ELEMENTS = 6
    WAIT_TIME = 10  # seconds

    DATE_POS = 0
    CLOSE_PRICE_ADJ_POS = 5

    BASE_URL = "https://au.finance.yahoo.com/"
    DRIVER_LOC = "E:\\Programming\\Python\\DerivativeSecurities\\res\\chromedriver.exe"

    def __init__(self):
        self.driver = webdriver.Chrome(self.DRIVER_LOC)
        self.driver.quit()

    def find_stock_prices(self, target_code, predictor_codes, duration):
        """Creates and returns a Dataframe of historical stock prices of the given stock_codes"""

        data = pd.DataFrame.from_dict(self.get_data(target_code, duration), orient="index",
                                      columns=[target_code.upper()])

        for stock_code in predictor_codes:
            data[stock_code.upper()] = self.get_data(stock_code, duration).values()

        return data

    def get_data(self, stock_code, duration):
        """Returns a dictionary of historical stock prices of the specified stock_code"""
        self.driver = webdriver.Chrome(self.DRIVER_LOC)
        self.driver.get(self.BASE_URL)

        self.navigate_to_stock(stock_code)
        start_date = self.set_start_date(duration)

        if not start_date:
            return False

        self.scroll_to_date(start_date)
        return self.read_data()

    def navigate_to_stock(self, stock_code):
        """Navigates to the page of the specified stock_code"""

        search_bar = self.driver.find_element_by_id("yfin-usr-qry")
        search_bar.send_keys(stock_code)
        search_bar.send_keys(Keys.RETURN)

    def set_start_date(self, duration):
        """Sets and returns the specified start date for the historical time period"""

        try:
            driver_wait = WebDriverWait(self.driver, self.WAIT_TIME)

            driver_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[text()='Historical data']"))).click()
            driver_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//table[@data-test='historical-prices']")))
            driver_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']"))).click()
            driver_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@data-value='%s']" % duration))).click()
            driver_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[text()='Apply']"))).click()
            element = driver_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']")))
            start_date = re.search("(.*) - .*", element.text).group(1)

            return self.validate_start_date(start_date)

        except TimeoutException:
            print("f")
            self.driver.quit()
            return False

    @staticmethod
    def validate_start_date(start_date):
        """Moves start_date to weekday if it falls on Saturday on Sunday"""

        # Yahoo Finance uses abbreviated month names where month names exceed 4 characters
        try:
            if datetime.strptime(start_date, '%d %B %Y').weekday() < 5:
                return start_date
        except ValueError:
            if datetime.strptime(start_date, '%d %b %Y').weekday() < 5:
                return start_date

        start_date = f"{int(start_date[:2]) + 2:02d}" + start_date[2:]
        return start_date

    def scroll_to_date(self, start_date):
        """Continuously scrolls to the bottom of the page until all records are loaded"""

        element = self.driver.find_element_by_tag_name('html')
        while True:
            try:
                # print(driver.execute_script("return document.body.scrollHeight"))

                self.driver.find_element_by_xpath(f"//span[text()='{start_date}']")
                break
            except NoSuchElementException:
                element.send_keys(Keys.END)

    def read_data(self):
        """Reads and returns a dictionary of all records (ignores Dividends)"""

        price_dict = dict()
        table = self.driver.find_element_by_xpath("//table[@data-test='historical-prices']")

        for row in table.find_elements_by_tag_name("tr"):
            elements = row.find_elements_by_tag_name("td")
            if len(elements) < self.NUM_ELEMENTS:
                continue
            price_dict[elements[self.DATE_POS].text] = float(elements[self.CLOSE_PRICE_ADJ_POS].text.replace(",", ""))

        self.driver.quit()
        return price_dict
