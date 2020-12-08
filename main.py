import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


DRIVER_LOC = "C:\\Program Files (x86)\\msedgedriver.exe"


def main():
    index_codes = []

    stock_code = get_code()[0]
    index_codes.extend(get_code())

    data = pd.DataFrame.from_dict(get_data(stock_code), orient="index",
                                  columns=[stock_code.upper()])
    data = data.rename_axis("Date")
    for code in index_codes:
        data[code.upper()] = get_data(code).values()

    print(data.to_string())
    input()


def get_data(stock_code):

    driver = webdriver.Edge(DRIVER_LOC)
    driver.get("https://au.finance.yahoo.com/")

    navigate_to_stock(driver, stock_code)

    start_date = set_start_date(driver)

    if not start_date:
        return False

    scroll_to_date(driver, start_date)
    return read_data(driver)


def navigate_to_stock(driver, code):

    search_bar = driver.find_element_by_id("yfin-usr-qry")
    search_bar.send_keys(code)
    search_bar.send_keys(Keys.RETURN)


def set_start_date(driver):

    try:
        driver_wait = WebDriverWait(driver, 10)

        driver_wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//span[text()='Historical data']"))).click()
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


def read_data(driver):

    price_dict = dict()
    table = driver.find_element_by_xpath("//table[@data-test='historical-prices']")

    for row in table.find_elements_by_tag_name("tr"):
        elements = row.find_elements_by_tag_name("td")
        if len(elements) < 6:
            continue
        price_dict[elements[0].text] = float(elements[5].text.replace(",", ""))

    driver.quit()
    return price_dict


def get_code():
    return input("Enter Desired Stock Code: ").split(" ")


if __name__ == '__main__':
    main()
