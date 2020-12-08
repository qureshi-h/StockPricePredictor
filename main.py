from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

DRIVER_LOC = "C:\\Program Files (x86)\\msedgedriver.exe"


def main():
    driver = webdriver.Edge(DRIVER_LOC)
    driver.get("https://au.finance.yahoo.com/quote/AAPL?p=AAPL")

    # code = get_code()
    # navigate_to_stock(driver, code)

    start_date = set_start_date(driver)
    # scroll_to_date(driver, start_date)
    stock_prices = get_data(driver)
    for key, value in stock_prices.items():
        print(key, value)
    input()
    driver.quit()


def navigate_to_stock(driver, code):

    search_bar = driver.find_element_by_id("yfin-usr-qry")
    search_bar.send_keys(code)
    search_bar.send_keys(Keys.RETURN)


def set_start_date(driver):

    try:
        driver_wait = WebDriverWait(driver, 10)

        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//li[@data-test='HISTORICAL_DATA']"))).click()
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//table[@data-test='historical-prices']")))
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']"))).click()
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@data-value='5_Y']"))).click()
        driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[text()='Apply']"))).click()
        element = driver_wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']")))
        start_date = re.search("(.*) - .*", element.text).group(1)
        return start_date

    except TimeoutException:
        print("f")
        # driver.quit()
        return False


def scroll_to_date(driver, start_date):
    element = driver.find_element_by_tag_name('html')
    while True:
        try:
            driver.find_element_by_xpath(f"//span[text()='{start_date}']")
            break
        except NoSuchElementException:
            element.send_keys(Keys.END)


def get_data(driver):

    price_dict = dict()
    table = driver.find_element_by_xpath("//table[@data-test='historical-prices']")
    for row in table.find_elements_by_tag_name("tr"):
        elements = row.find_elements_by_tag_name("td")
        if len(elements) < 6:
            continue
        price_dict[elements[0].text] = elements[5].text

    return price_dict


def get_soup(url):
    return BeautifulSoup(requests.get(url).text, "html.parser")


def get_code():
    return "aapl"
    return input("Enter Desired Stock Code")


if __name__ == '__main__':
    main()
