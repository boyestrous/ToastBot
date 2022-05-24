import datetime
import os
from unicodedata import category
from helpers import *
import pandas as pd


def main():
    """
        Entrypoint for the toast bot
    """
    logger.debug('all_to_CSV _main_')

    df = pd.DataFrame()
    driver = scraper.start_webdriver()


    startDate = datetime.datetime(2022,3,31)
    time_step = datetime.timedelta(days=5)

    while startDate > datetime.datetime(2022,1,1,0,0):
        ## start webdriver and setup the reports page to show the desired info
        endDate = startDate + time_step
        
        scraper.set_custom_dates(driver,startDate,endDate)

        # remove problematic elements from the page before scraping anything
        scraper.clean_page(driver)
        
        ## validate the tables and data sets are still as expected
        # TODO write validation checks
            # check types of td fields

        ## get categories from Toast, in case Firebase doesn't have a match later (see add_categories_to_items)
        toast_category_df = scraper.get_categories_from_toast(driver)

        ## Scrape the Toast page for items and orders during the selected time period
        order_details_html = scraper.scan_page(driver)

        four_week_df = soup.extract_orders_from_order_details(order_details_html)
        
        ## Add helper columns
        # Flags - used to identify actions that must be taken to resolve conflicts or issues (ex: missing category)
        df_with_helpers = data.add_helper_columns(four_week_df)

        # Add categories column to allow splitting items into different groups for manipulation
        df_with_categories = data.add_categories_to_items(df_with_helpers,toast_category_df)

        # df = pd.concat([df,df_with_categories])
        df_with_categories.to_csv('data_for_powerBI.csv', mode='a')
    
        startDate = startDate - time_step


    
        
        

    # manipulate item data into correct format
   

if __name__ == '__main__':
    import logging
    from logging.config import fileConfig
    fileConfig('./logging_config.ini')
    logger = logging.getLogger('core')
    main()