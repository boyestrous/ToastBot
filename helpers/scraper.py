# Functions that manipulate the selenium driver object for web scraping

# Logger Setup
import logging
from logging.config import fileConfig

from helpers import data
from helpers.general import format_date_for_toast
fileConfig('./logging_config.ini')
logger = logging.getLogger('scraper')

# Imports specific to this set of functions
import datetime
import os
import time
from dotenv import load_dotenv
from typing import Union
from webdriver_manager.chrome import ChromeDriverManager
import re

## Selenium imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_webdriver():
    """
        Launch a Chrome Window and return a driver object for future parsing and window manipulation
    """
    logger.debug('start_webdriver')
    # TODO allow 'headless' parameter
    ### chrome_options is really only necessary if you plan to enable additional features. It defaults to None. 
    ### it's setup here for easy un-commenting of the headless options
    chrome_options = webdriver.ChromeOptions()
    # ## Enable these options for headless server configuration (Heroku)
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,options=chrome_options)
    return driver
    

def check_driver(driver):
    """
        Returns an active driver object after performing a simple test to ensure the driver that was passed is still active.
               
        If errors occur - starts a new session and returns the NEW active driver
    """
    logger.debug('check_driver')

    ### if unable to access this property, the window has been closed and we'll be unable to proceed.
    try:
        driver.current_window_handle
        return driver
    except:
        logger.info('no current driver, launching new')
        driver = start_webdriver()
        return driver


def toast_login(driver, URL):
    """
        Sends credentials to Toast Login screen before fully resolving the page.
        Expects the URL provided to be "behind" authentication


        Requires vars.env to be present in the current working directory for passwords
            TOAST_USER: username for Toast
            TOAST_PASS: password for provided username

        returns after resolving past login screen
    """
    logger.debug('toast_login')

    #Get username and password from .env
    cwd = os.getcwd()
    load_dotenv(cwd + '/vars.env')
    toast_user = os.getenv('TOAST_USER')
    toast_pass = os.getenv('TOAST_PASS')

    # Selenium wait object, used to check conditions before proceeding
    wait = WebDriverWait(driver, timeout=10)

    ### Navigate to passed URL, which should be "behind" a login screen
    driver.get(URL)
    wait.until(lambda x: x.find_element(By.ID, "username")) # wait for html id of the username input field to be visible
    driver.find_element(By.ID,'username').send_keys(toast_user)
    driver.find_element(By.NAME,'password').send_keys(toast_pass)
    driver.find_element(By.NAME, 'action').click()
    wait.until(EC.url_matches(URL)) # done when url fully resolves to passed URL
    return driver


def set_custom_dates(driver,startDate:Union[str,datetime.datetime], endDate: Union[str,datetime.datetime]):
    """
        @param startDate (datetime or string in format: mm-dd-yyyy)
        @param endDate (datetime or string in format: mm-dd-yyyy)
        From the Toast Sales Reports screen:
            set the date dropdown to allow custom date entries
            enter start and end dates 
            load the report
        Returns active driver element with this page laoded

    """
    logger.debug('set_custom_date_mode')

    start = format_date_for_toast(startDate)
    end = format_date_for_toast(endDate)

    ### This function must run on the order-details reports screen
    # check the URL and redirect if the driver is somewhere else
    sales_order_details_URL = 'https://www.toasttab.com/restaurants/admin/reports/home#sales-order-details'
    
    # verify driver before proceeding
    driver = check_driver(driver)

    if driver.current_url != sales_order_details_URL:
        try: 
            driver.get(sales_order_details_URL)
            if driver.title == 'Sign In with Toast':
                logger.debug('webdriver is not authenticated - redirecting to toast_login')
                driver = toast_login(driver,sales_order_details_URL)
        except Exception as e:
            logger.critical(f'webdriver failure - set_custom_date_mode - {e}')
            return e.args
            
    # Selenium wait object, used to check conditions before proceeding
    wait = WebDriverWait(driver, timeout=10)
    
    time.sleep(4)
    driver.execute_script("scrollTo(0,0)")

    # Iterate through options until "custom" and then click to select
    date_drop = wait.until(EC.element_to_be_clickable((By.ID, "date-dropdown-container")))
    date_drop.click()
    el = driver.find_element(By.ID,'date-dropdown-container')
    for option in el.find_elements(By.TAG_NAME,'li'):
        # print(option.text)
        if option.text == 'Custom Date':
            option.click() # select() in earlier versions of webdriver
            break
   
    # Set the start and end dates for the custom range
    wait.until(lambda x: x.find_element(By.NAME, "reportDateStart"))   
    start_date = wait.until(EC.element_to_be_clickable((By.NAME, "reportDateStart")))
    start_date.click()
    start_date.send_keys(Keys.CONTROL + "a")
    start_date.send_keys(start)

    end_date = wait.until(EC.element_to_be_clickable((By.NAME, "reportDateEnd")))
    end_date.click()
    end_date.send_keys(Keys.CONTROL + "a")
    end_date.send_keys(end)
    end_date.send_keys(Keys.TAB)

    # Reload page with the selected dates
    update = wait.until(EC.element_to_be_clickable(((By.ID,'update-btn'))))
    update.click()
    details_tab = wait.until(EC.element_to_be_clickable((By.LINK_TEXT,'Order Details')))
    details_tab.click()

    return driver

def filter_preorders_only(driver):
    """
        Sets an additional filter for dining-options
            - Phone Order
            - Online Order
        If one of the dates in the range is in the past, we have to filter out the POS sales because they don't have all of the required fields
    """

    # Selenium wait object, used to check conditions before proceeding
    wait = WebDriverWait(driver, timeout=10)

    ## Select "More" Dropdown and search for "Dining Option" filter
    driver.find_element(By.CLASS_NAME,'multiselect').click()
    multi_options = driver.find_element(By.CLASS_NAME,'multiselect-container').find_elements(By.TAG_NAME,'input')
    for opt in multi_options:
        if opt.get_attribute('value') == 'diningOption':
            opt.click()
            opt.send_keys(Keys.TAB)
    
    ## Select the dining option dropdown that appears and click both options for pre-orders
    dining_option_dropdown = wait.until(EC.element_to_be_clickable(((By.ID,'dining-option-option'))))
    dining_option_dropdown.click()
    dining_options = dining_option_dropdown.find_element(By.CLASS_NAME,'multiselect-container').find_elements(By.TAG_NAME,'input')
    for do in dining_options:
        if do.get_attribute('value') == '500000002795776616' or do.get_attribute('value') == '500000002795776612':
            do.click()
    do.send_keys(Keys.TAB)
    update = wait.until(EC.element_to_be_clickable(((By.ID,'update-btn'))))
    update.click()

    wait.until(lambda x: x.find_element(By.ID, "top-items")) 
    return driver

def clean_page(driver):
    """
        Remove Toast pop-ups, chat FAB, sidebars, etc. that get in the way of the webdriver as its moving through the pages
    """
    logger.debug('clean_page')
    # TODO document classes and ids in this list and how to add new items
    js = 'var cls = [".embeddedServiceHelpButton","#left-rail",".flex",".w-screen",".fixed bottom-0","list-none m-0 flex",".wootric-footer"]; for (var i=0;i<cls.length;i++) {console.log(cls[i]); if (document.querySelector(cls[i])) {document.querySelector(cls[i]).style.display = "none";} }'
    driver.execute_script(js)
    return driver

def save_orders_html(driver) -> str:
    """
        returns the innerHTML content of the order-details-section of the current page
        Selenium is very slow at parsing all of the details on each page, so this function
        saves the html content for later parsing by BS4
    """
    logger.debug('save_orders_html')

    # Selenium wait object, used to check conditions before proceeding
    wait = WebDriverWait(driver, timeout=10)

    order_details_section = wait.until(EC.presence_of_element_located((By.ID,'order-details-section')))
    order_html = order_details_section.get_attribute('innerHTML')
    return order_html

def scan_page(driver):
    """
        Read through the order_details and determine how many pages
    """
    logger.debug('scan_page')

    # pages list will hold the html of each page for later parsing
    order_details_html = []

    # Selenium wait object, used to check conditions before proceeding
    wait = WebDriverWait(driver, timeout=10)

    ## Find the order_details section and count the pages that contain order details
    order_page_selector = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'pagination')))
    pages = order_page_selector[1].find_elements(By.TAG_NAME, 'li')
    page_count = pages[len(pages)-2].text
    logger.debug('page count: %s', page_count)

    ## Iterate through the pages and grab the relevant data
    if page_count == '1':
        logger.debug('only 1 page')
        order_details_html.append(save_orders_html(driver))
    else:
        logger.debug('page: 1')
        # Grab page 1
        order_details_html.append(save_orders_html(driver))

        parent_class = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")

        # loop through subsequent pages
        # for i in range(1,int(page_count)):
            # logger.debug(f'page: {i}')
        while (parent_class.get_attribute("class") != "next disabled"):
            
            
            # This is one of the only consistent objects inside the order-details-section.
            # When it's visible, the order details tables are also visible
            paginator = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")))

            # click to move to next page (Toast is sometimes very slow)
            # driver.find_element(By.XPATH,f"//div[@class='pagination'][1]/ul/li/a[contains(.,{i+1})]").click()
            next_button = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]/a")
            next_button.click()

            # the paginator element will go stale when the order details *start* to switch pages
            wait.until(EC.staleness_of(paginator))
            # wait until the pagination element is located again before saving the html
            wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")))
            
            order_details_html.append(save_orders_html(driver))

            parent_class = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")
    
    # Save a copy of the most recent html structure for testing
    with open('helpers/tests/latest_order_details.html','w', encoding="utf-8") as file:
        logger.debug('order_html saved to file')
        file.write(order_details_html[0])

    return order_details_html


def get_categories_from_toast(driver):
    """
        Update list of items and associated categories from the Menu Item Summary at the top of the page

        returns an array of objects {'item': item, 'category': category}
    """
    logger.debug('get_categories_from_toast')

    # Selenium wait object, used to check conditions before proceeding
    wait = WebDriverWait(driver, timeout=10)
    
    # Iterate through options until "100" and then click to select
    wait.until(lambda x: x.find_element(By.ID, "top-items_length"))
    driver.find_element(By.ID,'top-items_length').find_element(By.CLASS_NAME,'btn-group').click()
    category_count = driver.find_element(By.ID,'top-items_length').find_element(By.CLASS_NAME,'btn-group')
    dd_menu = category_count.find_element(By.CLASS_NAME,'dropdown-menu')
    for option in dd_menu.find_elements(By.TAG_NAME,'li'):
        if (option.text == '100'):
            option.find_element(By.TAG_NAME,'a').click()
            break
    
    # find the top-items table and grab data to make a list of item-category matches
    categories = []
    table = driver.find_element(By.ID,'top-items')
    rows = table.find_element(By.TAG_NAME,'tbody').find_elements(By.TAG_NAME,'tr')
    for row in rows:
        tds = row.find_elements(By.TAG_NAME,'td')
        item = tds[0].text
        category = tds[1].text
        categories.append({'item_name': item, 'category': category})
    return data.convert_list_to_df(categories) 

def validate_order_details_columns():
    return True