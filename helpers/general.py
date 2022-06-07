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

    # Allow strings in several formats (I've found all of these in the website in the past)
    if type(date) == str:
        converted_date = ''
        for fmt in ('%m/%d/%Y','%m/%d/%y','%m-%d-%Y','%m-%d-%y'):
            # stop after successful conversion
            if converted_date == '':
                try:
                    converted_date = datetime.datetime.strptime(date, fmt)
                except ValueError:
                    pass
        # If it hasn't converted after the for loop, it failed
        if converted_date == '':
            raise ValueError("string does not match a valid date format, use mm-dd-yy or mm-dd-yyyy")
        
        final_string = converted_date.strftime('%m-%d-%Y')
    elif type(date) == datetime.datetime:
        final_string = date.strftime('%m-%d-%Y')
    else:
        raise Exception(f'invalid data type{type(date)}, datetime or string required')


    return final_string
