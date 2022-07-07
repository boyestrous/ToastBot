import datetime
import pytest
from selenium import webdriver
import selenium
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException

from helpers.scraper import check_driver, get_categories_from_toast, scan_page, set_custom_dates, start_webdriver, toast_login


@pytest.fixture
# TODO figure out how to launch ONE driver and run all of the following tests that don't involve testing the driver itself
def driver():
    chrome_options = webdriver.ChromeOptions()
    service = Service(executable_path=ChromeDriverManager().install())
    _driver = webdriver.Chrome(service=service,options=chrome_options)
    yield _driver
    _driver.quit()

def test_old_webdriver_exception(driver):
    with pytest.raises(SessionNotCreatedException):
        service  = Service(executable_path=r"./helpers/tests/chromedriver")
        driver = webdriver.Chrome(service=service) 

# def test_check_driver(driver):
#     assert driver == check_driver(driver)


@pytest.mark.slow
def test_failed_driver_check_driver(driver):
    """IF a driver is quit/orphaned, a NEW driver should be created and returned"""
    #capture session id before closing passed driver
    default_driver_id = driver.session_id 
    driver.quit()
    # call function and pass a closed webdriver
    new_driver = check_driver(driver)
    new_driver_id = new_driver.session_id
    new_driver.quit() #cleanup before finishing test
    assert default_driver_id != new_driver_id

def test_URL_match_toast_login(driver):
    """
        The returned driver needs to be past the authentication wall
        Failed login or other exceptions (handled elsewhere) will return a login url instead
    """
    URL = 'https://www.toasttab.com/restaurants/admin/reports/home#sales-order-details'
    returned_driver = toast_login(driver,URL)
    returned_url = returned_driver.current_url
    assert returned_url == URL


def test_correct_dates_set_custom_dates(driver):
    """
        Ensure passed dates were actually applied to the reports webpage
    """
    #set dates and convert to the correct string format
    startDate = datetime.datetime.today() - datetime.timedelta(days=10)
    endDate = startDate + datetime.timedelta(days=5)
    startDateText = startDate.strftime('%m-%d-%Y')
    endDateText = endDate.strftime('%m-%d-%Y')

    returned_driver = set_custom_dates(driver, startDate, endDate)

    assert returned_driver.find_element(By.NAME, 'reportDateStart').get_attribute('value') == startDateText
    assert returned_driver.find_element(By.NAME, 'reportDateEnd').get_attribute('value') == endDateText


def test_bad_strings_set_custom_dates(driver):
    """
        If we pass garbage strings, we want an error instead of failing to copy the new date values
    """
    #set dates and convert to the correct string format
    startDate = 'tomorrow'
    endDate = 'may 1, 2022'

    with pytest.raises(Exception):
        set_custom_dates(driver,startDate, endDate)


def test_alternate_datestring_set_custom_dates(driver):

    startDate = '05/01/2022'
    endDate = '05/03/2022'

    returned_driver = set_custom_dates(driver, startDate, endDate)

    assert returned_driver.find_element(By.NAME, 'reportDateStart').get_attribute('value') == '05-01-2022'
    assert returned_driver.find_element(By.NAME, 'reportDateEnd').get_attribute('value') == '05-03-2022'

@pytest.mark.single
def test_get_categories_from_toast(driver):
    """
        Should return a dataframe with two columns: Item, Category
    """
    startDate = datetime.datetime.today() + datetime.timedelta(days=1)
    endDate = startDate + datetime.timedelta(days=4)
    returned_driver = set_custom_dates(driver, startDate, endDate)

    return_df = get_categories_from_toast(returned_driver)
    assert return_df.columns[0] == 'item_name'
    assert return_df.columns[1] == 'category'
    assert return_df.columns[2] == 'qty'
    assert return_df.size > 1

def test_scan_page(driver):
    """
        Should return a list of strings that are html objects. List length should match the number of pages with order details
    """
    # Past date with known quantity of pages (5)
    driver = set_custom_dates(driver,'09/01/2020','09/01/2020')

    pages_html = scan_page(driver)

    assert len(pages_html) == 5
    assert type(pages_html[0]) == str