# Functions that manipulate data retrieved through scraping or elsewhere

# Logger Setup
import logging
from logging.config import fileConfig

from helpers import alerts, fire
fileConfig('./logging_config.ini')
logger = logging.getLogger('data')


# Imports specific to this set of functions
import pandas as pd
import os

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
    # flagged items show up in notifications on the front-end and changes are processed in firebase functions
    df.loc[df['category'].isna(),'flags']='category missing'
    
    # if there are any missing categories, use the ones from the toast website as a placeholder
    missing_cats = df[df['category'].isna()]
    df.dropna(subset=['category'], inplace=True)
    logger.debug(f'missing cats size: {missing_cats.size}')
    missing_cats.dropna(subset=['item_name','order_id'],inplace=True)
    if (len(missing_cats.index) > 0):
        alerts.send_sms_alert('missing categories need to be reviewed')
        filename = 'missing_cats.csv'
        missing_cats.to_csv('missing_cats.csv', mode='a', header=(not os.path.exists(filename)))
        # apply the category that was scraped
        df2 = scraped_categories_df.merge(missing_cats, left_on='item_name', right_on="item_name", how='right')
        df2.drop(columns=['category_y'], inplace=True)
        df2.rename(columns={'category_x':'category'}, inplace=True)

        df=pd.concat([df,df2])

    return df