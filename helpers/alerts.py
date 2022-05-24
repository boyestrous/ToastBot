# Functions that read html data with the Bs4 module

# Logger Setup
import logging
from logging.config import fileConfig

fileConfig('./logging_config.ini')
logger = logging.getLogger('alerts')



def send_sms_alert(message):
    """
        sends an SMS 
    """
    logger.debug('send_sms_alert')
    logger.critical(message)
    