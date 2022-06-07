import datetime
import os
from unicodedata import category
from helpers import *


def main():
    """
        Entrypoint for the toast bot
    """
    logger.debug('core _main_')
    
    ## start webdriver and setup the reports page to show the desired info
    startDate = datetime.datetime.today() + datetime.timedelta(days=1)
    endDate = startDate + datetime.timedelta(days=1)
    driver = scraper.start_webdriver()
    scraper.set_custom_dates(driver,startDate,endDate)

    # remove problematic elements from the page before scraping anything
    scraper.clean_page(driver)
    
    ## get categories from Toast, in case Firebase doesn't have a match later (see add_categories_to_items)
    toast_category_df = scraper.get_categories_from_toast(driver)

    ## Scrape the Toast page for items and orders during the selected time period
    # historical dates will include POS sales, so we need to exclude them if we're running a report that includes past dates
    if startDate < datetime.datetime.today() or endDate < datetime.datetime.today():
        scraper.filter_preorders_only(driver)
    order_details_html = scraper.scan_page(driver)
    
    df= soup.extract_orders_from_order_details(order_details_html)

    ## Add helper columns
    # Flags - used to identify actions that must be taken to resolve conflicts or issues (ex: missing category)
    df = data.add_helper_columns(df)

    # TODO add known weird orders handler (States Attorney, etc.)
    # Add categories column to allow splitting items into different groups for manipulation
    df = data.add_categories_to_items(df,toast_category_df)
    df = data.expand_customer_info(df)
    df = data.manipulate_df_strings(df)
    df = data.expand_datetime(df)
    
    ## Handle the modifiers for each category
    df = data.handle_donut_rows(df)
    
    
    # extract order details and item modifiers for non-donuts
        # check for cinnamon rolls with buttercream frosting
    # prep dfs for upload
        # merge donut items and orders with other items and orders
        # split orders and items into two separate dfs
    # check for fallen orders
        # find orders that are in firebase, but not the most recent order list
        # open a new webdriver and go to the order lookup page
        # search for each order, copy order details content to a order_continer_list
        # souper: extract details from order_container_list
            # if order status == voided -> update firebase
            # TODO orders don't have a status right now, toasty_web will need to filter
            # if items different -> delete or add as needed
    # TODO firebase logs - "last run 5/11 at 3:00am"
    # TODO firebase messages web interface - "errors occurred"
        
        

    # manipulate item data into correct format


if __name__ == '__main__':
    import logging
    from logging.config import fileConfig
    fileConfig('./logging_config.ini')
    logger = logging.getLogger('core')
    main()