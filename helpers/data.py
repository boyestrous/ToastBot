# Functions that manipulate data retrieved through scraping or elsewhere

# Logger Setup
import logging
from logging.config import fileConfig

from sniffio import current_async_library

from helpers import alerts, fire
fileConfig('./logging_config.ini')
logger = logging.getLogger('data')


# Imports specific to this set of functions
import pandas as pd
import os
import re

def convert_list_to_df(object_list: list) -> pd.DataFrame:
    """
        converts a list of category objects into a dataframe
        deduplicates
        exports to CSV (see heroku memory limitations)
    """
    logger.debug('convert_list_to_df')

    df = pd.DataFrame(object_list)
    df = df.drop_duplicates()
    return df

def add_helper_columns(df: pd.DataFrame):
    """
        Helper columns will store useful info for a user
    """
    logger.debug('add_helper_columns')

    # flags will be used to identify items that need attention. Example: an item missing a category
    df['flags'] = ''
    return df

def add_categories_to_items(items_df:pd.DataFrame, scraped_categories_df:pd.DataFrame):
    """
        Get category/item matches from firebase and merge them into the dataframe with the items
        Firebase categories will overwrite items with 
    """
    logger.debug('add_categories_to_items')

    ## Get category-item pairs from firebase
    cats = fire.get_categories()
    # ensure the order of columns stays consistent
    cats = cats[['item_name','category']]
    cats['item_name'].drop_duplicates(inplace=True)

    # Merge the dfs, keeping the category from firebase and the item details from the scraper
    df = cats.merge(items_df, left_on='item_name', right_on="item_name", how='right')

     
    ## If item doesn't have a matched category from firebase, flag it for follow-up 
    # copy the rows with missing categories to their own dataframe
    missing_cats = df.copy()[df['category'].isna()]
    df.dropna(subset=['category'], inplace=True)
    missing_cats.dropna(subset=['item_name','order_id'],inplace=True)
    if (len(missing_cats.index) > 0):
        logger.warning(f'there are at least {len(missing_cats.index)} items without categories')
        alerts.send_sms_alert('missing categories need to be reviewed')
        
        # flagged items show up in notifications on the front-end and changes are processed in firebase functions
        df.loc[df['category'].isna(),'flags']='category missing'
        
        # make a csv for later review or append list to existing csv
        filename = 'missing_cats.csv'
        missing_cats.to_csv('missing_cats.csv', mode='a', header=(not os.path.exists(filename)))

        # use the categories that were scraped from the toast website as a placeholder
        df2 = scraped_categories_df.merge(missing_cats, left_on='item_name', right_on="item_name", how='right')
        df2.drop(columns=['category_y'], inplace=True)
        df2.rename(columns={'category_x':'category'}, inplace=True)
        df=pd.concat([df,df2])

    return df

def expand_customer_info(df:pd.DataFrame) -> pd.DataFrame:
    """
        Extracts customer details from the *horrible* text string from Toast
    """
    logger.debug('expand_customer_info')

    #create new DF for manipulation
    cust_ext = pd.DataFrame()
    cust_ext['customer'] = df['customer']
    #the next 4 rows: set regex for extract, compile regex for replacement, extract, remove

    #order type
    type_regex = "(?P<order_type>.{1,20})\:"
    ctype_regex = re.compile(r"(?P<order_type>.{1,20})\:",flags=re.IGNORECASE)
    cust_ext['order_type'] = cust_ext['customer'].str.extract(type_regex, re.IGNORECASE)
    df['customer'] = df['customer'].str.replace(ctype_regex,'')

    #phone
    phone_regex = "(?P<phone>\d{3}\-\d{3}\-\d{4})"
    cphone_regex = re.compile(r"(?P<phone>\d{3}\-\d{3}\-\d{4})",flags=re.IGNORECASE)
    cust_ext['phone'] = cust_ext['customer'].str.extract(phone_regex, re.IGNORECASE)
    df['customer'] = df['customer'].str.replace(cphone_regex,'')

    #email
    email_regex = "(?P<email>\S{1,25}@\S{1,25})"
    cemail_regex = re.compile(r"(?P<email>\S{1,25}@\S{1,25})",flags=re.IGNORECASE)
    cust_ext['email'] = cust_ext['customer'].str.extract(email_regex, re.IGNORECASE)
    df['customer'] = df['customer'].str.replace(cemail_regex,'')

    #remove \n from text strings
    cslash = re.compile(r"\n", flags=re.IGNORECASE)
    df['customer'] = df['customer'].str.replace(cslash,'')
    df['customer'] = df['customer'].str.strip()

    #name
    cname_regex = re.compile(r"(?P<name>.{1,100})\b\s{1,50}\(detail\)",flags=re.IGNORECASE)
    cust_ext['name'] = df['customer'].str.extract(cname_regex)
    df['customer'] = df['customer'].str.replace(cname_regex,'')
    df['customer'] = df['customer'].str.strip()

    #delivery
    df['delivery instructions'] = df['customer']
    del_regex = '(?P<address>.{1,100}61\d{3})\s{1,100}(?P<delivery_instructions>\S.{1,100})'
    del_ext = pd.DataFrame(df['delivery instructions'])
    del_ext = del_ext['delivery instructions'].str.extract(del_regex)
    df = pd.concat([df, del_ext], axis=1)
    df = df.drop(['delivery instructions'],axis=1)

    #drop unnecessary fields
    cust_ext = cust_ext[['order_type','phone','email','name']]
    #merge dataframes
    df = pd.concat([df, cust_ext], axis=1)
    df.drop(['customer'],axis=1, inplace=True)
    return df

def expand_datetime(df):
    """
        Extracts date and time that an order is due, accepts strings from either pre-orders or walk-ins 
    """
    logger.debug('expand_datetime')

    #pull due date/time
    due_regex = '(?P<date>\d{1,2}\/\d{1,2}\/\d{2,4}).+(?P<time>\d{1,2}\:\d{2}.+[AP]M)'
    due_ext = pd.DataFrame(df['datetime'])
    due_ext = df['datetime'].str.extract(due_regex, re.IGNORECASE)
    df = pd.concat([df, due_ext[['date', 'time']]], axis=1)

    # remove the original combined column
    df.drop(['datetime'],axis=1, inplace=True)

    # FIXME uniform formatting for timestrings mm/dd/yyyy is the correct format

    return df

def handle_donut_rows(df:pd.DataFrame):
    """
        Manipulates the donut rows and returns the a df with expanded rows and columns.
            "Assorted dozen" rows are split into 12 rows of single donuts (preset varieties)
            Sprinkles and special requests are extracted from the mods column
    """
    logger.debug('handle_donut_rows')

    # All categories that are used in Toast to sell donuts
    donut_categories = ['Donuts']

    # Create a copy to avoid Pandas SettingWithCopyWarning
    donut_df = df.copy()
    donut_df = donut_df[donut_df['category'].isin(donut_categories)] #only keep the donut rows
    df = df[~df['category'].isin(donut_categories)] # drop the donut rows from the original df
    
    # convert assorted dozens into the specific donuts
    donut_df = unassort_donuts(donut_df)

    return pd.concat([df,donut_df])

def manipulate_df_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
        Converts all currency strings in the dataframe to floats
        returns a dataframe with currency strings converted to floats
    """
    currency_columns = [
        'unit_price',
        'discount',
        'taxes',
        'net_price',
        'total_price',
        'refund_amt',
        ]

    # All currency columns have a $ at the start, strip this out and convert to float
    for column in currency_columns:
        if df[column].dtype != 'string':
            df[column] = df[column].astype('string')
        df[column] = df[column].apply(lambda x: float(x.replace('$','')))

    return df

def unassort_donuts(donut_df: pd.DataFrame) -> pd.DataFrame:
    """
    Turns a count of assorted dozen donuts into a list of the individual donuts
    returns original DF with the new rows appended and Assorted Dozens removed
    """
    logger.debug('unassort_donuts')

    # make an new DF with only Assorted Dozens
    df = donut_df.copy()
    df = df[df['item_name'] == 'Assorted Dozen Donuts']
    
    # delete existing item_name and mods columns
    df.drop(columns=['item_name','mods'], inplace=True)

    # add a column with a list of the flavors in the standard assorted dozen
    standard_dozen = [
        ['Long John', 'Chocolate'],
        ['Long John', 'Vanilla'], 
        ['Long John', 'Maple'], 
        ['Ring Donut', 'Glaze'],
        ['Ring Donut', 'Chocolate'],
        ['Cake Donut', 'Chocolate'], 
        ['Twist Donut', 'Cinnamon Glaze'],
        ['Twist Donut', 'Vanilla'],
        ['Fried Roll', 'Glaze'], 
        ['Apple Fritter', 'Glaze'], 
        ['Bismark (filled donut)', 'Bavarian'], 
        ['Bismark (filled donut)', 'Rasp with White Icing']
        ]

    # explode list column so each row has a different item and mods object
    df['pre_assort'] = [standard_dozen for _ in range(len(df))]
    df = df.explode('pre_assort')

    # create two new columns 'item_name', 'mods'
    df[['item_name','mods']] = pd.DataFrame(df['pre_assort'].tolist(), index=df.index)
    df.drop(columns=['pre_assort'], inplace=True)
 
    # update the unit_price, net_price, taxes, discount to 1/12 of their original values
    df['unit_price'] = df['unit_price'].apply(lambda x: x/12)
    df['discount'] = df['discount'].apply(lambda x: x/12)
    df['taxes'] = df['taxes'].apply(lambda x: x/12)
    df['net_price'] = df['net_price'].apply(lambda x: x/12)
    df['total_price'] = df['total_price'].apply(lambda x: x/12)
    df['refund_amt'] = df['refund_amt'].apply(lambda x: x/12)

    # remove the original 'assorted dozen' rows
    df = df[df['item_name'] != 'Assorted Dozen Donuts']

    # combine with non-assorted dozen rows
    df = pd.concat([df,donut_df[donut_df['item_name'] != 'Assorted Dozen Donuts']])

    return df

def handle_cookie_mods(cookie_df):
    
    return cookie_df