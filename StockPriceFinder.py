import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

NUM_ELEMENTS = 6
WAIT_TIME = 10  # seconds

DATE_POS = 0
CLOSE_PRICE_ADJ_POS = 5

BASE_URL = "https://au.finance.yahoo.com/"
DRIVER_LOC = "C:\\Program Files (x86)\\msedgedriver.exe"


def find_stock_prices(stock_codes):
    """Creates and returns a Dataframe of historical stock prices of the given stock_codes"""

    data = pd.DataFrame.from_dict(get_data(stock_codes[0]), orient="index",
                                  columns=[stock_codes[0].upper()])

    for stock_code in stock_codes[1:]:
        data[stock_code.upper()] = get_data(stock_code).values()

    return data


def get_data(stock_code):
    """Returns a dictionary of historical stock prices of the specified stock_code"""

    driver = webdriver.Edge(DRIVER_LOC)
    driver.get(BASE_URL)

    navigate_to_stock(driver, stock_code)
    start_date = set_start_date(driver)

    if not start_date:
        return False

    scroll_to_date(driver, start_date)
    return read_data(driver)


def navigate_to_stock(driver, stock_code):
    """Navigates to the page of the specified stock_code"""

    search_bar = driver.find_element_by_id("yfin-usr-qry")
    search_bar.send_keys(stock_code)
    search_bar.send_keys(Keys.RETURN)


def set_start_date(driver):
    """Sets and returns the specified start date for the historical time period"""

    try:
        driver_wait = WebDriverWait(driver, WAIT_TIME)

        driver_wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//span[text()='Historical data']"))).click()
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//table[@data-test='historical-prices']")))
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']"))).click()
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@data-value='1_Y']"))).click()
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='Apply']"))).click()
        element = driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']")))
        start_date = re.search("(.*) - .*", element.text).group(1)

        return start_date

    except TimeoutException:
        print("f")
        driver.quit()
        return False


def scroll_to_date(driver, start_date):
    """Continuously scrolls to the bottom of the page until all records are loaded"""

    element = driver.find_element_by_tag_name('html')
    while True:
        try:
            # print(driver.execute_script("return document.body.scrollHeight"))

            driver.find_element_by_xpath(f"//span[text()='{start_date}']")
            break
        except NoSuchElementException:
            element.send_keys(Keys.END)


def read_data(driver):
    """Reads and returns a dictionary of all records (ignores Dividends)"""

    price_dict = dict()
    table = driver.find_element_by_xpath("//table[@data-test='historical-prices']")

    for row in table.find_elements_by_tag_name("tr"):
        elements = row.find_elements_by_tag_name("td")
        if len(elements) < NUM_ELEMENTS:
            continue
        price_dict[elements[DATE_POS].text] = float(elements[CLOSE_PRICE_ADJ_POS].text.replace(",", ""))

    driver.quit()
    return price_dict
