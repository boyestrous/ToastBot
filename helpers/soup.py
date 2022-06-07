# Functions that read html data with the Bs4 module

# Logger Setup
import logging
from logging.config import fileConfig



fileConfig('./logging_config.ini')
logger = logging.getLogger('data')

# Imports from this module
from helpers import alerts
from helpers.data import convert_list_to_df


# Imports specific to this set of functions
import bs4
from bs4 import BeautifulSoup



def extract_orders_from_order_details(order_details_pages):
    """
        Takes a list of html content previously extracted from the Toast Order Details Page
        Returns a df with each row being an item from an order
            order_ids are also attached to each individual item
    """
    logger.debug('extract_orders_from_order_details')
    
    # TODO add scraped_categories parameter, compare item counts from the soup to the scraped_category counts (to make sure nothing was missed or double-counted)
    # Ex: the top of the toast page says the orders had 68 long johns, we should find a total of 68 long johns in the soup

    # this will be used to store item objects until they are converted to a DF and returned 
    order_list = []

    for page in order_details_pages:
        soup = BeautifulSoup(page, 'html.parser')

        # each order sits inside an element with this class.
        order_containers = soup.find_all('div', {"class": "order-border"})
        
        for container in order_containers:
            ## Gather the order details from the information above the details section
            # This is the completely unique ID that can be used to lookup orders elsewhere. Strip off the ID: from the beginning for safe storage
            order_id = container.find('div', {"class": "order-detail-meta-id"}).get_text().strip().replace('ID: ','')
            logger.debug('id: %s', order_id)

            # Order status is surrounded by parentheses
            order_status = container.find('h4').find('span').get_text().replace('(','').replace(')','')

            # Friendly IDs are NOT unique
            order_friendly_id = container['id']

            # All customer info in a *horrible* text string - we'll clean it up later with Regex
            # Expect to find the following fields:
                # Order Type (Online, Phone, Take-Out, Delivery)
                # Customer Phone
                # Customer Email (maybe)
                # Customer Name (maybe)
                # Customer Address (maybe)
            cust_info = container.find_all('div', {"class": "span5"})[0].get_text().strip()
            
            ## Date and time are stored in different places for pre-orders 
            if cust_info != '':
                ## Pre-orders have customer info
                # All date/time due in ANOTHER *horrible* text string - we'll clean it up later with Regex (see data.py)
                datetime = container.find_all('div', {"class": "span3"})[3].get_text().strip()
            else: 
                ## walk-in orders don't have customer info, so we use time opened as the datetime
                datetime =  container.find('div',{'class':'check-server-details'}).get_text().strip()


            ## Gather the item details from the item table
            order_table = container.find('table', id='order-details-item-table')

            ## Validate that the columns haven't changed in the order-details table
            validate_columns(order_table)           

            # each row of the table holds an item and its details
            rows = order_table.find_all('tr')
            if rows[1].has_attr('id'):
                order_list.append(handle_special_rows(rows))
            else:
                for row in rows[1:]:                              
                    logger.debug(f'order id: {order_id}')
                    row_values = row.find_all('td')

                    if len(row_values) < 1:
                        logger.debug('rows less than 1')
                        raise Exception(f'row_values missing: {order_id}')
                    # Expected tds in each order table: 
                    # 0, Name of item
                    # 1, unit price
                    # 2, quantity
                    # 3, discount
                    # 4, net price
                    # 5, tax
                    # 6, total
                    # 7, voided?
                    # 8, reason
                    # 9, refunded?                
                    item_name = row_values[0].string.strip()
                    cookie_mods = row_values[1].string
                    unit_price = row_values[2].string.strip()
                    cookie_qty = int(row_values[3].string.replace(',','').strip())
                    discount = row_values[4].string.strip()
                    net_price = row_values[5].string.strip()
                    taxes = row_values[6].string.strip()
                    total_price = row_values[7].string.strip()
                    voided = row_values[8].string
                    reason = row_values[9].string
                    refund_qty = int(row_values[10].string.replace(',','').strip())
                    refund_amt = row_values[11].string.strip()
                    order_list.append({'order_id':order_id,'order_friendly_id':order_friendly_id,'order_status':order_status,'item_name':item_name, 'qty':cookie_qty,'unit_price':unit_price, 'discount':discount, 'net_price':net_price, 'taxes':taxes, 'total_price':total_price, 'reason':reason, 'refund_qty':refund_qty, 'refund_amt':refund_amt, 'mods':cookie_mods, 'customer': cust_info, 'datetime': datetime, 'voided': voided})

    return convert_list_to_df(order_list)

def validate_columns(order_table):
    ## Validate that the columns haven't changed in the order-details table
    expected_columns = ['Menu Item', 'Modifiers', 'Price', 'Qty', 'Discount', 'Net', 'Tax', 'Total', 'Voided?', 'Reason', 'Refund Qty', 'Refund']
    actual_columns = []
    
    for col in order_table.find_all('th'):
        actual_columns.append(col.text)
    if expected_columns != actual_columns:
        alerts.send_sms("expected columns don't match in Toast")
        raise Exception('columns on order-details-table have changed')
    else: 
        logger.debug('columns confirmed')

def handle_special_rows(rows):
    """
        Extract data from non-standard order tables
            Gift cards have extra rows in-between the expected ones

    """
    logger.debug('handle_special_rows')
    # logger.debug(f'row: {row}')

    # row_values = row.find_all('td')

    # if len(row_values) < 1:
    #     logger.debug('rows less than 1')
    #     raise Exception(f'row_values missing: {order_id}')
    # # Expected tds in each order table: 
    # # 0, Name of item
    # # 1, unit price
    # # 2, quantity
    # # 3, discount
    # # 4, net price
    # # 5, tax
    # # 6, total
    # # 7, voided?
    # # 8, reason
    # # 9, refunded?                
    # item_name = row_values[0].string.strip()
    # cookie_mods = row_values[1].string
    # unit_price = row_values[2].string.strip()
    # cookie_qty = int(row_values[3].string.strip())
    # discount = row_values[4].string.strip()
    # net_price = row_values[5].string.strip()
    # taxes = row_values[6].string.strip()
    # total_price = row_values[7].string.strip()
    # voided = row_values[8].string
    # reason = row_values[9].string
    # refund_qty = int(row_values[10].string.strip())
    # refund_amt = row_values[11].string.strip()
    return {}