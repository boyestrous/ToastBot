# Logger Setup
import logging
from logging.config import fileConfig

fileConfig('./logging_config.ini')
logger = logging.getLogger('scraper')

# Imports for this file
import re
import datetime

def format_date_for_toast(date):
    """
        Takes a string or datetime object and returns in the format needed for copying into toast mm-dd-yyyy
    """
    logger.debug('format_date_for_toast')
    # Allow strings in mm-dd-yyyy or mm/dd/yyyy format for easy CLI testing
    if type(date) == str:
        # replace / with -, for dates formatted mm/dd/yyyy
        date = re.sub('/','-',date)

        # before returning, make sure it strictly fits the expected string format
        proper_string = re.search(r"\d{2}\-\d{2}\-\d{4}", date)
        # re.search will return None if it doesn't find the expected pattern
        if not proper_string:
            raise Exception('string is not proper date format. Use mm-dd-yyyy')
        
        final_string = date
    elif type(date) == datetime.datetime:
        final_string = date.strftime('%m-%d-%Y')


    return final_string
