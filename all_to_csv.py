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

    # TODO convert this into parameters that can run on the core.py. No need to have a separate file for this...
    df = pd.DataFrame()
    driver = scraper.start_webdriver()


    startDate = datetime.datetime(2021,2,3)
    time_step = datetime.timedelta(days=5)

    while startDate > datetime.datetime(2021,1,1,0,0):
        ## start webdriver and setup the reports page to show the desired info
        endDate = startDate + time_step
        logger.debug(f'dates: {startDate} to {endDate}')
        
        scraper.set_custom_dates(driver,startDate,endDate)

        # remove problematic elements from the page before scraping anything
        scraper.clean_page(driver)

        ## get categories from Toast, in case Firebase doesn't have a match later (see add_categories_to_items)
        toast_category_df = scraper.get_categories_from_toast(driver)
        

        ## Scrape the Toast page for items and orders during the selected time period
        order_details_html = scraper.scan_page(driver)

        order_details_df = soup.extract_orders_from_order_details(order_details_html)
        
        ## Add helper columns
        # Flags - used to identify actions that must be taken to resolve conflicts or issues (ex: missing category)
        df_with_helpers = data.add_helper_columns(order_details_df)

        # Add categories column to allow splitting items into different groups for manipulation
        df_with_categories = data.add_categories_to_items(df_with_helpers,toast_category_df)

        # df = pd.concat([df,df_with_categories])
        filename = 'data_for_powerBI.csv'
        # df.to_csv(filename, index=False, mode='a', header=(not os.path.exists(filename)))
        df_with_categories.to_csv('data_for_powerBI.csv', mode='a', header=(not os.path.exists(filename)))
    
        startDate = startDate - time_step


    
        
        

    # manipulate item data into correct format
   

if __name__ == '__main__':
    import logging
    from logging.config import fileConfig
    fileConfig('./logging_config.ini')
    logger = logging.getLogger('core')
    main()