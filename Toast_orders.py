import datetime
import logging
import time
import selenium
import threading
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import pickle
import os
import os.path
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

### Custom Modules ###
import fire

# MOVED TO Scraper.py 5/10/22
# def start_webdriver():
#     chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument('--disable-gpu')
#     # chrome_options.add_argument('--headless')
#     # chrome_options.add_argument('--no-sandbox')
#     # chrome_options.add_argument('--disable-dev-shm-usage')

#     service = Service(executable_path=ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service)
#     logger.info('webdriver started')

#     return driver

# MOVED TO Scraper.py 5/10/22
# def toast_login(driver, URL):
#     driver.get(URL)
#     WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "username")))
#     time.sleep(3)
#     # TODO remove find_element(s)_by_* deprecated commands
#     driver.find_element(By.ID,'username').send_keys(toast_user)
#     driver.find_element(By.NAME,'password').send_keys(toast_pass)
#     driver.find_element(By.NAME, 'action').click()

# MOVED TO Scraper.py 5/11/22
# def set_custom_date_mode():
#     time.sleep(2)
#     driver.find_element(By.ID,'date-dropdown-container').click()
#     el = driver.find_element(By.ID,'date-dropdown-container')
#     for option in el.find_elements(By.TAG_NAME,'li'):
#         # print(option.text)
#         if option.text == 'Custom Date':
#             option.click() # select() in earlier versions of webdriver
#             break

# MOVED TO Scraper.py 5/11/22
# def set_dates(start, end):
#     """
#     takes full datestrings with the format mm-dd-yyyy
#     """
#     time.sleep(3)

#     date_pickers = driver.find_elements(By.CLASS_NAME,'datepicker')
#     start_date = driver.find_element(By.NAME, "reportDateStart")
#     start_date.click()
#     start_date.send_keys(Keys.CONTROL + "a")
#     start_date.send_keys(start)

#     end_date = driver.find_element(By.NAME, "reportDateEnd")
#     end_date.click()
#     time.sleep(0.5)
#     end_date.send_keys(Keys.CONTROL + "a")
#     end_date.send_keys(end)
#     end_date.send_keys(Keys.TAB)
    # date_pickers = driver.find_elements(By.CLASS_NAME,'datepicker')
    # start_date = driver.find_element(By.NAME"reportDateStart")
    # start_date.click()
    # for day in date_pickers[0].find_elements(By.CLASS_NAME,'day'):
    #     logger.info('date picker text: %s', day.text)
    #     if day.text == start and day.get_attribute("class") != "day old" and datetime.date.today().day <= int(start):
    #         logger.info('requested date number is higher than today. Look at this month')
    #         day.click() # select() in earlier versions of webdriver
    #         start_date.send_keys(Keys.ENTER)
    #         break
    #     if day.text == start and day.get_attribute("class") == "day new" and datetime.date.today().day > int(start):
    #         logger.info('requested date is lower than today. Look at next month')
    #         day.click() # select() in earlier versions of webdriver
    #         start_date.send_keys(Keys.ENTER)
    #         break

    # end_date = driver.find_element(By.NAME"reportDateEnd")
    # end_date.click()  
    # for day in date_pickers[1].find_elements(By.CLASS_NAME,'day'):
    #     if day.text == end and day.get_attribute("class") != "day old":
    #         day.click() # select() in earlier versions of webdriver
    #         end_date.send_keys(Keys.TAB)
    #         break

# MOVED TO Scraper.py 5/11/22 
# def load_report():
#     update = driver.find_element(By.ID,'update-btn')
#     update.click()
#     time.sleep(3)
#     driver.find_element(By.LINK_TEXT,'Order Details').click()

# MOVED TO Scraper.py 5/11/22 
# def get_categories():
#     time.sleep(2)
#     driver.find_element(By.ID,'top-items_length').find_element(By.CLASS_NAME,'btn-group').click()
#     category_count = driver.find_element(By.ID,'top-items_length').find_element(By.CLASS_NAME,'btn-group')
#     dd_menu = category_count.find_element(By.CLASS_NAME,'dropdown-menu')
#     for option in dd_menu.find_elements(By.TAG_NAME,'li'):
#         if (option.text == '100'):
#             option.find_element(By.TAG_NAME,'a').click()
#             break
#     categories = []
#     table = driver.find_element(By.ID,'top-items')
#     rows = table.find_element(By.TAG_NAME,'tbody').find_elements(By.TAG_NAME,'tr')
#     for row in rows:
#         tds = row.find_elements(By.TAG_NAME,'td')
#         item = tds[0].text
#         category = tds[1].text
#         categories.append({'item': item, 'category': category})
#     cats = pd.DataFrame(categories)
#     cats = cats.drop_duplicates()
#     cats.to_csv('item_categories.csv')


# MOVED TO SOUP.py on 5/16/2022
# def souper(soup):
#     # order_list = []
#     orders_to_delete = []

#     order_containers = soup.find_all('div', {"class": "order-border"})
#     iterator = 1
#     for container in order_containers:
#         order_id = container.find('div', {"class": "order-detail-meta-id"}).get_text().strip()
#         order_friendly_id = container['id']
#         if any(d['order_friendly_id'] == order_friendly_id for d in order_list):
#             order_friendly_id = order_friendly_id + '(' + str(iterator) + ')'
#             # logger.debug('order id exists: %s', order_friendly_id)
#             iterator += 1
#         cust_info = container.find_all('div', {"class": "span5"})[0].get_text().strip()
#         due = container.find_all('div', {"class": "span3"})[3].get_text().strip()
#         logger.debug('due: %s', due)
#         logger.debug('id: %s', order_friendly_id)
#         order_tables = container.find_all('table', id='order-details-item-table')
#         # logger.debug('order tables count: %s', len(order_tables))
#         i = 1
#         for order in order_tables:
#             rows = order.find_all('tr')
#             logger.debug('rows found: %s', len(rows))

#             for row in rows[1:]:
#                 logger.debug('row: %s', row)
#                 tval = row.find_all('td')
#                 # Expected tds in each order table:
#                 # 1, Name of item
#                 # 2, unit price
#                 # 3, quantity
#                 # 4, discount
#                 # 5, net price
#                 # 6, tax
#                 # 7, total
#                 # 8, voided?
#                 # 9, reason
#                 # 10, refunded?                
#                 if tval[10].string.strip() != 'true' and tval[8].string.strip() != 'true':
#                     item_name = tval[0].string.strip()
#                     logger.debug(item_name)
#                     cookie_mods = tval[1].string
#                     # FIXME numbers over 1000 have a comma in the string: ex: 4,500
#                     cookie_qty = int(tval[3].string.strip())
#                     voided = tval[8].string.strip()
#                     order_list.append({'item_key':i,'order_id':order_id,'order_friendly_id':order_friendly_id,'item_name':item_name, 'qty':cookie_qty, 'mods':cookie_mods, 'customer': cust_info, 'due': due, 'voided': voided})
#                     i = i + 1
#                 else: 
#                     orders_to_delete.append(order_id_fixer(order_id))
    
#     # delete orders and items that only have voided/refunded stuff

#     # make a comparison list of the ids from the order_list
#     order_list_ids = []
#     for order in order_list:
#         order_list_ids.append(order_id_fixer(order['order_id']))
    
#     # only delete orders if they have NO MORE ITEMS
#     # Voided items themselves will be filtered out when pulled (via javascript)
#     orders_to_delete = list(set(orders_to_delete)) # make a unique list
#     for o in orders_to_delete:
#         while o in order_list_ids:
#             try:
#                 print('need to remove: ', o)
#                 orders_to_delete.remove(o)
#             except:
#                 break

#     if len(orders_to_delete) > 0:
#         fire.delete_voided_orders_and_items(orders_to_delete)
#     # FIXME - remove after fixing
#     # return {'list':order_list, 'delete': orders_to_delete}

# MOVED TO SCRAPER.py 5/16/2022
# def order_id_fixer(order_id:str):
#     return order_id.replace('ID: ', '')

# MOVED TO SCRAPER.PY 5/12
# def pager():
#     ods = driver.find_element(By.ID,'order-details-section')
#     logger.debug('ods: %s', ods)
#     pages.append(ods.get_attribute('innerHTML'))
#     time.sleep(3)

# MOVED TO SCRAPER.PY 5/12
# def paginator():
#     #grab categories of the items from the top table before reading the order lists
    
#     WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "order-details-section")) 


#     # get_categories()
#     #hide help button, it gets in the way of the page next click
#     js = 'var cls = [".embeddedServiceHelpButton","#left-rail",".flex",".w-screen",".fixed bottom-0","list-none m-0 flex"]; for (var i=0;i<cls.length;i++) {console.log(cls[i]); if (document.querySelector(cls[i])) {document.querySelector(cls[i]).style.display = "none";} }'
#     driver.execute_script(js)
#     order_page_selector = driver.find_elements(By.CLASS_NAME,'pagination')[1]
#     pages = order_page_selector.find_elements(By.TAG_NAME, 'li')
#     page_count = pages[len(pages)-2].text
#     logger.info('page count: %s', page_count)
#     parent_class = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")
#     if page_count == '1':
#         logger.debug('only 1 page')
#         pager()
#         print('one page')
#     else:
#         while (parent_class.get_attribute("class") != "next disabled"):
#             print('paginator multiple pages')
#             logger.debug('paginator while loop entered')
#             parent_class = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")
#             time.sleep(3)
#             pager()
#             next_button = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]/a")
#             next_button.click()
#             logger.debug('NEXT CLICKED')
#             parent_class = driver.find_element(By.XPATH,"//div[@class='pagination'][1]/ul/li[last()]")
#     logger.debug('paginator complete')

# MOVED TO SCRAPER.PY 5/12
# def filter_preorders_only():
#     driver.find_element(By.CLASS_NAME,'multiselect').click()
#     multi_options = driver.find_element(By.CLASS_NAME,'multiselect-container').find_elements(By.TAG_NAME,'input')
#     for opt in multi_options:
#         if opt.get_attribute('value') == 'diningOption':
#             opt.click()
#             opt.send_keys(Keys.TAB)
#     dining_option_dropdown = driver.find_element(By.ID,'dining-option-option')
#     dining_option_dropdown.click()
#     dining_options = dining_option_dropdown.find_element(By.CLASS_NAME,'multiselect-container').find_elements(By.TAG_NAME,'input')
#     for do in dining_options:
#         if do.get_attribute('value') == '500000002795776616' or do.get_attribute('value') == '500000002795776612':
#             do.click()
#     do.send_keys(Keys.TAB)
#     driver.find_element(By.ID,'update-btn').click()

#     WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "top-items")) 
#     return


# MOVED TO SCRAPER/SOUP.PY 5/16/2022
# def parse(sdate, edate):
#     """
#         set mode, dates, load report, iterate through pages and grab HTML content for later parsing
#     """
    
#     # logger.debug('parse function started')
#     # sdate = sdate
#     # edate = edate
#     # global pages
#     # global order_list
#     # # set_custom_date_mode()
#     # # set_dates(sdate, edate)
#     # # load_report()

#     # # historical dates will include POS sales, so we need to exclude them if we're running a report that includes past dates
#     # if datetime.datetime.strptime(sdate,'%m-%d-%Y') < datetime.datetime.today() or datetime.datetime.strptime(edate,'%m-%d-%Y') < datetime.datetime.today():
#         # filter_preorders_only()

#     order_list = []
#     pages=[]
#     paginator()
#     for count, page in enumerate(pages):
#         print('page no: ', count)
#         soup = BeautifulSoup(page, 'html.parser')
#         souper(soup)

 

def extract_details_from_mods(df):
    #create a dataframe and manipulate fields to get cleaner data
    df = df
    #pull out wrapping instructions from mods list
    # logger.debug('df from extract: %s', df)
    wrap_regex = "([^,]{1,15}wrap[^,\b]{1,25})"
    wrapping_extract = pd.DataFrame(df['mods'])
    wrapping_extract['wrapping'] = df['mods'].str.extract(wrap_regex, re.IGNORECASE)
    df = pd.concat([df, wrapping_extract['wrapping']], axis=1)

    ## Customers moved data.py 6/2/2022
    # #create new DF for manipulation
    # cust_ext = pd.DataFrame()
    # cust_ext['customer'] = df['customer']
    # #the next 4 rows: set regex for extract, compile regex for replacement, extract, remove
    # #order type
    # type_regex = "(?P<order_type>.{1,20})\:"
    # ctype_regex = re.compile(r"(?P<order_type>.{1,20})\:",flags=re.IGNORECASE)
    # cust_ext['order_type'] = cust_ext['customer'].str.extract(type_regex, re.IGNORECASE)
    # df['customer'] = df['customer'].str.replace(ctype_regex,'')
    # #phone
    # phone_regex = "(?P<phone>\d{3}\-\d{3}\-\d{4})"
    # cphone_regex = re.compile(r"(?P<phone>\d{3}\-\d{3}\-\d{4})",flags=re.IGNORECASE)
    # cust_ext['phone'] = cust_ext['customer'].str.extract(phone_regex, re.IGNORECASE)
    # df['customer'] = df['customer'].str.replace(cphone_regex,'')
    # #email
    # email_regex = "(?P<email>\S{1,25}@\S{1,25})"
    # cemail_regex = re.compile(r"(?P<email>\S{1,25}@\S{1,25})",flags=re.IGNORECASE)
    # cust_ext['email'] = cust_ext['customer'].str.extract(email_regex, re.IGNORECASE)
    # df['customer'] = df['customer'].str.replace(cemail_regex,'')

    # #remove \n from text strings
    # cslash = re.compile(r"\n", flags=re.IGNORECASE)
    # df['customer'] = df['customer'].str.replace(cslash,'')
    # df['customer'] = df['customer'].str.strip()

    # #name
    # cname_regex = re.compile(r"(?P<name>.{1,100})\b\s{1,50}\(detail\)",flags=re.IGNORECASE)
    # cust_ext['name'] = df['customer'].str.extract(cname_regex)
    # df['customer'] = df['customer'].str.replace(cname_regex,'')
    # df['customer'] = df['customer'].str.strip()

    # #delivery
    # df['delivery instructions'] = df['customer']
    # del_regex = '(?P<address>.{1,100}61\d{3})\s{1,100}(?P<delivery_instructions>\S.{1,100})'
    # del_ext = pd.DataFrame(df['delivery instructions'])
    # del_ext = del_ext['delivery instructions'].str.extract(del_regex)
    # df = pd.concat([df, del_ext], axis=1)
    # df = df.drop(['delivery instructions'],axis=1)
    # # print('cols after del steps: ',df.columns)

    # #drop unnecessary fields
    # cust_ext = cust_ext[['order_type','phone','email','name']]
    # #merge dataframes
    # df = pd.concat([df, cust_ext], axis=1)
    # df = df.drop(['customer'],axis=1)

    #pull BG color from mods
    bg_regex = '([^,]{1,15})\sbackground'
    bg_color_ext = pd.DataFrame(df['mods'])
    bg_color_ext['bg_color'] = df['mods'].str.extract(bg_regex, re.IGNORECASE)
    bg_color_ext = bg_color_ext[['bg_color']]
    df = pd.concat([df, bg_color_ext], axis=1)

    # FIXME "Any color" is not being picked up. It stops at "color"
    #extract writing color from mods
    # writing_regex = '([^,\s]{1,15})\swriting'
    # writing_color_ext = pd.DataFrame(df['mods'])
    # writing_color_ext['writing_color'] = df['mods'].str.extract(writing_regex, re.IGNORECASE)
    # writing_color_ext = writing_color_ext[['writing_color']]
    # df = pd.concat([df, writing_color_ext], axis=1)

    #pull sprinkles from mods
    sprink_regex = '(?P<sprinkles>([^,]{1,25}\s)?sprinkles)'
    sprink_color_ext = pd.DataFrame(df['mods'])
    sprink_color_ext = df['mods'].str.extract(sprink_regex, re.IGNORECASE)
    df = pd.concat([df, sprink_color_ext['sprinkles']], axis=1)

    # MOVED TO Data.py 6/2/2022
    # #pull due date/time
    # due_regex = '(?P<date>\d{1,2}\/\d{1,2}\/\d{4}).+(?P<time>\d{1,2}:\d\d AM|\d{1,2}:\d\d PM)'
    # due_ext = pd.DataFrame(df['due'])
    # due_ext = df['due'].str.extract(due_regex, re.IGNORECASE)
    # df = pd.concat([df, due_ext[['date', 'time']]], axis=1)
    # print(df.head())

    #strip out previously extracted content and extras
    cwrap_regex = re.compile(r"([^,]{1,15}wrap[^,\b]{1,25})", flags=re.IGNORECASE)
    cbg_regex = re.compile(r"([^,]{1,15})\sbackground", flags=re.IGNORECASE)
    # cwriting_regex = re.compile(r"([^,\s]{1,15})\swriting", flags=re.IGNORECASE)
    csprink_regex = re.compile(r"(?P<sprinkles>([^,]{1,25}\s)?sprinkles)", flags=re.IGNORECASE)
    cchar_regex = re.compile(r"(\d{1,3}-\d{1,3} Characters)", flags=re.IGNORECASE)
    cnodraw_regex = re.compile(r"(no drawings)", flags=re.IGNORECASE)
    ccomma_regex = re.compile(r"(\s?,\s?)", flags=re.IGNORECASE)
    df['other_requests'] = df['mods']
    df['other_requests'] = df['other_requests'].str.replace(cwrap_regex,'')
    df['other_requests'] = df['other_requests'].str.replace(cbg_regex,'')
    # df['other_requests'] = df['other_requests'].str.replace(cwriting_regex,'')
    df['other_requests'] = df['other_requests'].str.replace(csprink_regex,'')
    df['other_requests'] = df['other_requests'].str.replace(cchar_regex,'')
    df['other_requests'] = df['other_requests'].str.replace(cnodraw_regex,'')
    df['other_requests'] = df['other_requests'].str.replace(ccomma_regex,'')
    df['item_name'] = df['item_name'].str.replace("Round Iced Sugar Cookies",'Round Iced')
    df['item_name'] = df['item_name'].str.replace("Round Custom Cookie",'Round Iced')
    df['item_name'] = df['item_name'].str.replace("Custom Round",'Round Iced')
    df['item_name'] = df['item_name'].str.replace("Round Iced Cookie",'Round Iced')


    # strip 'ID: ' from the front of the order ID
    # # df.loc[:,('order_id')] = df.loc[:,('order_id')].str.extract(r'([0-9]{1,19})',re.IGNORECASE)
    # df['order_id'] =  [re.sub(r'([0-9]{1,19})','', str(x)) for x in df['order_id']]

    df.rename(columns={"mods": "mods_archive"},inplace=True)
    df = df.drop(['due'],axis=1)
    # logger.info('dataframe manipulation complete')
    return df

class ParseThread(threading.Thread):
    def __init__(self,sdate,edate,out_type):
        self.progress = 0
        self.sdate = sdate
        self.edate = edate
        self.out_type = out_type
        self.result = ''
        logger.debug('ParseThread INIT')
        super().__init__()

    def run(self):
        logger.debug('ParseThread running')
        df = get_cookie_orders(self.sdate, self.edate, self.out_type)
            # if isinstance(self.progress, float) or isinstance(self.progress, int):
            #     print('progress: ',_)
            #     self.progress = _
            # else: 
            #     print('RESULT')
            #     self.result = _

# MOVED TO DATA.py 5/17/2022
# def handle_categories(df):
#     """
#         get category/item matches from firebase and merge them into the dataframe with the items

#         dataframe passed must have item_name field
#     """
#     #add categories to dataframe before any further manipulation is done
#     cats = pd.DataFrame(fire.get_categories())
#     cats['item_name'].drop_duplicates(inplace=True)
#     logger.debug('df before merging categories')
#     logger.debug(df)
#     logger.debug('cats df')
#     logger.debug(cats)
#     df = pd.merge(df, cats, left_on='item_name', right_on='item_name')
#     missing_cats = df[df['category'].isna()]
#     if (len(missing_cats.index) > 0):
#         missing_cats.to_csv('missing_cats.csv')
#         logger.warn('Missing categories, check missing_cats.csv for details')
#     df.dropna(subset = ['category'], inplace=True)
#     return df

def get_cookie_orders(sdate, edate, out_type='df'):
    """
        Primary function controlling subtasks for reading the Toast page.

    """
    global df

    # holding via csv between functions helps reduce memory errors in Heroku
    if os.path.exists('hold_df.csv'):
        os.remove("hold_df.csv")
    logger.debug('get_cookie_orders function started')
    sdate = sdate
    edate = edate
    out_type = out_type
    logger.debug('sdate: %s', sdate)
    logger.debug('edate: %s', edate)
    logger.debug('out_type: %s', out_type)
    parse(sdate, edate)

    df = pd.DataFrame(order_list)
    df_with_cats = handle_categories(df)

    logger.debug('df before sending to csv')
    logger.debug(df_with_cats)
    df_with_cats.to_csv('hold_df.csv')
    return df_with_cats

# def return_df(out_type):
#     if os.path.exists('hold_df.csv'):
#         # read from csv b/c memory objects don't persist long enough on low-resource deployments (like heroku)
#         df = pd.read_csv('hold_df.csv')

#         # TODO get donut pars, join with donut_df 'case' (second column)
#         #set donut DF before extract function. They won't have bg_color, etc.
#         donut_df = df[df['category'].isin(['Donuts'])]
#         logger.debug('donut df category sort complete')
#         # logger.debug(donut_df)
#         donut_df.rename(columns={"other_requests": "mods"},inplace=True)
#         donut_df.fillna('',inplace=True)
#         donut_df.drop_duplicates()
#         donut_df = unassort(donut_df)
#         donut_df = donut_df[['item_name', 'mods', 'qty']].groupby(['item_name','mods']).sum()
#         #split assorted dozens into their individual donuts, then merge into donut_df

#         logger.debug('donut df ready')

#         #extract relevant cookie and delivery details from the mods field 
#         df = extract_details_from_mods(df)

#         # build cookie_df
#         cookie_df = df[df['category'].isin(['Round', 'Shapes','Custom','Open Cake', 'Frequent Shapes','Spring Holiday Shapes','Numbers','Sports','Summer Holiday Shapes','Winter Holiday Shapes','Fall Holiday Shapes'])]
#         logger.debug('cookie_df before combining')
#         logger.debug(cookie_df)
#         cookie_df = cookie_df[['item_name', 'wrapping', 'bg_color','sprinkles','other_requests','qty']]
#         cookie_df['bg_color'] = cookie_df['bg_color'].str.strip()
#         cookie_df['bg_color'] = cookie_df['bg_color'].fillna('Unknown - Check Notes')
#         cookie_df = cookie_df.fillna('')
#         cookie_df = cookie_df.groupby(['bg_color','item_name', 'sprinkles','wrapping','other_requests']).sum()
#         logger.debug('cookie_df to be returned: ')
#         logger.debug(cookie_df)

#         # get delivery list
#         delivery_df = df[['order_type','order_friendly_id','name','phone','email','delivery instructions', 'time']]
#         delivery_df = delivery_df.loc[delivery_df['order_type'] == 'Delivery'].drop_duplicates()

#         # TODO rolls list
#         # TODO danish and coffee cakes list

#         # Get list of names for orders
#         names_df = df[['order_type','order_friendly_id','name','time']].drop_duplicates().sort_values(by=['name'])
#         names_df = names_df.loc[names_df['order_type'] != 'Delivery']

#         if out_type == 'html':
#             return {
#                 'status': 'done',
#                 'count': len(df['order_friendly_id'].drop_duplicates()),
#                 'cookies':cookie_df.to_html(classes='table striped'),
#                 'deliveries':delivery_df.to_html(classes='table striped'),
#                 'names': names_df.to_html(classes='table striped'),
#                 'donuts': donut_df.to_html(classes='table striped'),
#                 'delivery_count': len(delivery_df['order_friendly_id'].drop_duplicates())}
#         if out_type == 'df':
#             return {'status': 'done','count': len(df['order_friendly_id'].drop_duplicates()), 'cookies':cookie_df,'deliveries':delivery_df, 'names':names_df, 'donuts': donut_df}
#     else:
#         return {'status': 'working'}

# MOVED TO data.py 6/6/2022
# def unassort(donut_df):
#     """
#     Turns a count of assorted dozen donuts into a list of the individual donuts, returns DF that can be merged back into the donut_df
#     """
#     # print(donut_df)
#     dozens = donut_df.loc[donut_df['item_name']=='Assorted Dozen Donuts'].sum()['qty']
#     dozens = int(dozens)

#     unassorted_donuts = pd.DataFrame(columns=['item_name', 'mods','qty'])

#     if dozens > 0:
#         print('asst doz qty: ', dozens)
#         donut_df = donut_df[donut_df['item_name'] != 'Assorted Dozen Donuts']
#         # print(donut_df)

#         #append a row for each donut type to a new dataframe
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Long John', 'mods':'Chocolate', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Long John', 'mods':'Vanilla', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Long John', 'mods':'Maple', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Ring Donut', 'mods':'Glaze', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Cake Donut', 'mods':'Chocolate', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Cake Donut', 'mods':'Maple', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Twist Donut', 'mods':'Vanilla', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Twist Donut', 'mods':'Cinnamon Glaze', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Fried Roll', 'mods':'Glaze', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Apple Fritter', 'mods':'', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Bismark (filled donut)', 'mods':'Bavarian', 'qty': dozens}, ignore_index=True)
#         unassorted_donuts = unassorted_donuts.append({'item_name' : 'Bismark (filled donut)', 'mods':'Rasp with White Icing', 'qty': dozens}, ignore_index=True)
#         print('unassorted: ',unassorted_donuts)
#         unassorted_donuts.rename(columns={"mods": "other_requests"},inplace=True)
#     return donut_df.append(unassorted_donuts)

def identify_fallen_orders(local_ids, dates):
    """
    A fallen order is an order that was previously added to firebase, but was not updated/"set" in the most recent push for that date range.

    This indicates that the order was either:
    A) Voided
    B) Not showing on the order-details screen - meaning the order should be there, but it isn't
    """
    fire_orders = fire.read_orders_from_firestore(dates['min'],dates['max'])
    
    fallen_orders = []

    for fire_id in fire_orders.keys():
        if fire_id not in local_ids:
            # TODO setup Logger for fire.py
            print('this order was already in firebase for this date range', fire_id, 'investigate further')
            fallen_orders.append(fire_id)

    return fallen_orders


def check_id(order_id):
    """
        From the order query page, searches for an order by the ID and returns a status object
        {status: 'string', data: ''}
    """
    logger.info('checking id: %s', order_id)

    order_id_box = driver.find_element(By.ID,'searchCriteria_orderId')

    order_id_box.clear()
    order_id_box.send_keys(order_id)
    order_id_box.send_keys(Keys.ENTER)
    
    WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "search-results")) 

    result_count = len(driver.find_elements(By.CLASS_NAME,'rounded-corners-4'))

    if result_count > 0 and result_count <= 1:
        try: 
            order_state = driver.find_elements(By.CLASS_NAME,'span4')[0]

            if order_state.text.find('Void') != -1:
                id_status = {'status': 'voided'}
            else:
                try: 
                    result_row_header = driver.find_element(By.CLASS_NAME,'result-header')
                    result_row_header.find_element(By.CLASS_NAME, 'span4').find_element(By.TAG_NAME,'a').click()

                    detail_modal = driver.find_element(By.ID,'order-detail')
                    time.sleep(1)
                    id_status = {'status':'updated', 'data': detail_modal.get_attribute('innerHTML')}
                    time.sleep(1)
                    
                    driver.get ('https://www.toasttab.com/restaurants/admin/checksearch#checkid')
                except Exception as e:
                    print('could not find missing ID from firebase :', order_id)
                    driver.implicitly_wait(10)
                    driver.get ('https://www.toasttab.com/restaurants/admin/checksearch#checkid')
                time.sleep(2)
        except Exception as e:
            fire.add_exception({
                'source':'fallen_order_finder',
                'exception':str(e),
                'datetime': datetime.datetime.now()
            })
        logger.info("id_status from check_id function: %s", id_status['status'])
    else:
        logger.info("id_status from check_id function: %s", id_status['status'])

    return id_status


def fallen_order_finder(ids=[]):
    global driver
    global toast_user
    global toast_pass
    cwd = os.getcwd()
    load_dotenv(cwd + '/vars.env')

    toast_pass = os.getenv('TOAST_PASS')

    toast_user = "parker@grovestreetbakery.com"

    driver = start_webdriver()
    
    driver.implicitly_wait(10)
    toast_login('https://www.toasttab.com/restaurants/admin/checksearch#checkid')
    WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "searchCriteria_orderId")) 

    # orders that are still active, need to collect information to update Firebase
    active_orders = []

    #voided orders need to be removed from Firebase
    voided_orders = []

    for order_id in ids:
        id_result = check_id(order_id)
        if id_result['status'] == 'voided':
            logger.info(f'id: {order_id} was voided')
            voided_orders.append(order_id)
        elif id_result['status'] == 'updated':
            active_orders.append(id_result['data'])
    
    try:
        driver.quit()
    except:
        logger.debug('no existing drivers')

    fire.delete_voided_orders_and_items(voided_orders)
    fallen_souper(active_orders)
        

def  fallen_souper(modals):
    order_list = []

    for modal in modals:
        soup = BeautifulSoup(modal,'html.parser')

        order_id = soup.find_all('div', {"class": "order-detail-meta-id"})[1].get_text().strip()
        cust_info = soup.find_all('div', {"class": "span5"})[0].get_text().strip()
        due = soup.find_all('div', {"class": "span3"})[3].get_text().strip()

        order_tables = soup.find_all('table', id='order-details-item-table')
        # print('order tables count: %s', order_tables)
    
        parent_node = soup.find('h4', id='order-summary-header')

        order_name = parent_node.find(text=True, recursive=False)
        order_friendly_id = re.findall(r'\#(?P<num>\d{1,4})', order_name)
        order_friendly_id = 'order-number-' + order_friendly_id[0]
        i = 1
        for order in order_tables:
            rows = order.find_all('tr')
            for row in rows[1:]:
                tval = row.find_all('td')
                item_name = tval[0].text.strip()
                cookie_mods = tval[1].string
                cookie_qty = int(tval[3].string.strip())
                voided = tval[8].string.strip()
                order_list.append({'item_key':i,'order_id':order_id,'order_friendly_id':order_friendly_id,'item_name':item_name, 'qty':cookie_qty, 'mods':cookie_mods, 'customer': cust_info, 'due': due, 'voided': voided})
                i = i + 1

    fallen_df = handle_categories(pd.DataFrame(order_list))

    fire.add_items_from_dict(fallen_df.to_dict('index'))

def dev_init():
    """
        Launches the Toast window and performs login. Use this if you want to test inidividual functions from the command line
    """
    global toast_pass
    global toast_user
    global google_creds
    global logger
    global df
    global Spreadsheet_ID
    global Cookie_Range
    global URL
    global driver
    global cookie_df
    global delivery_df
    global item_categories
    global parsing_threads
    global thread_id
    cookie_df = pd.DataFrame()
    delivery_df = pd.DataFrame()
    item_categories = []
    #get .env file from current directory
    cwd = os.getcwd()
    load_dotenv(cwd + '/vars.env')

    toast_pass = os.getenv('TOAST_PASS')

    toast_user = "parker@grovestreetbakery.com"

    # MOVED TO helpers.py 5/5/2022
    # logger = logging.getLogger('Toast2')
    # logger.setLevel(logging.DEBUG)
    # # create file handler which logs even debug messages
    # fh = logging.FileHandler('toast_v2_log.log')
    # fh.setLevel(logging.DEBUG)
    # # # create console handler with a higher log level
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.INFO)
    # # create formatter and add it to the handlers
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # ch.setFormatter(formatter)
    # # add the handlers to the logger
    # logger.addHandler(fh)
    # logger.addHandler(ch)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    df = pd.DataFrame()
    URL = 'https://www.toasttab.com/restaurants/admin/reports/home#sales-order-details'
    # logger.info('main function executed')

    driver = start_webdriver()

    driver.implicitly_wait(10)
    toast_login(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "date-dropdown-container")))
    logger.info('login complete')

def main():
    """
        Automated function calls the full set of commands and self-closes.
    """
    global toast_pass
    global toast_user
    global google_creds
    global logger
    global df
    global Spreadsheet_ID
    global Cookie_Range
    global URL
    global driver
    global cookie_df
    global delivery_df
    global item_categories
    global parsing_threads
    global thread_id

    cookie_df = pd.DataFrame()
    delivery_df = pd.DataFrame()
    item_categories = []
    #get .env file from current directory
    cwd = os.getcwd()
    load_dotenv(cwd + '/vars.env')

    toast_pass = os.getenv('TOAST_PASS')

    toast_user = "parker@grovestreetbakery.com"

    logger = logging.getLogger('Toast2')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('toast_v2_log.log')
    fh.setLevel(logging.DEBUG)
    # # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # try:
    #     driver.quit()
    # except:
    #     logger.debug('no existing drivers')

    df = pd.DataFrame()
    URL = 'https://www.toasttab.com/restaurants/admin/reports/home#sales-order-details'
    # logger.info('main function executed')

    driver = start_webdriver()
    driver.implicitly_wait(10)

    toast_login(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "date-dropdown-container")))
    logger.info('login complete')
   
    tomorrow = datetime.datetime.today() - datetime.timedelta(days=10)
    tom31 = tomorrow + datetime.timedelta(days=5)

    df = get_cookie_orders(tomorrow.strftime('%m-%d-%Y') ,tom31.strftime('%m-%d-%Y'))

    try: 
        donut_df = df.copy()
        donut_df = donut_df[donut_df['category'].isin(['Donuts'])]
        # strip 'ID: ' from the front of the order ID
        # donut_df.loc[:,('order_id')] = donut_df.loc[:,('order_id')].str.extract(r'([0-9]{1,19})',re.IGNORECASE)
        donut_df['order_id'] =  [re.sub(r'([0-9]{1,19})','', str(x)) for x in donut_df['order_id']]        
        donut_df.rename(columns={"mods": "other_requests"},inplace=True)
        donut_df.to_csv("donuts.csv")
        df = extract_details_from_mods(df)
        df.to_csv('output.csv')
    except Exception as e:
        exp_str = "Exception from orders: " + str(e)
        logger.warning(exp_str)

    try:
        driver.quit()
    except:
        logger.debug('no existing drivers')

    # export to CSV to try to handle Heroku resource problems. CSV storage between steps seems to reduce the memory errors.
    df.to_csv('output.csv')
    orders = df[['order_id','order_type','name','email','phone','date','time','address','delivery_instructions','order_friendly_id']].drop_duplicates()
    fire.add_orders_from_dict(orders.to_dict('index'))
    logger.info('Orders added to Firebase')
    
    logger.info('orders pushed, checking for ids that didnt get modified')
    fo = identify_fallen_orders(list(orders['order_id']), {'min':tomorrow,'max':tom31})
    if len(fo) > 0:
        logger.warning('Missing orders, starting the fallen order finder')
        logger.warning('Fallen orders list: %s', fo)
        fallen_order_finder(fo)
    else: 
        logger.info('No missing orders, proceeding to items')

    
    items = df[['item_key','order_id','order_friendly_id','item_name','category','voided','wrapping','bg_color','sprinkles','other_requests','qty']].drop_duplicates()
    items = items[items['category'] != 'Donuts']
    logger.info('items df size: %s',items.size)
    fire.add_items_from_dict(items.to_dict('index'))
    fire.add_items_from_dict(donut_df.to_dict('index'))
    logger.info('items added')

    logger.info('Done.')
    return 'Done!'
    # return True




if __name__ == '__main__':
    main()
    
# #pull contact info from customer field
# cust_regex = "(?P<order_type>.{1,100}):\\n(?P<phone>\d{3}-\d{3}-\d{4})(\\n)?(?P<email>.{1,100}\@.{1,100})?\\n(?P<cust_name>.{1,100})\(detail\)"
# cust_ext = customers['customer'].str.extract(cust_regex, re.IGNORECASE)
# cust_ext = cust_ext[['order_type', 'phone', 'email', 'cust_name']]
# customers = pd.concat([customers, cust_ext], axis=1)
# customers = customers.drop(['customer'],axis=1)

# delivery = customers.loc[customers['order_type'] == 'Delivery']
# delivery.count()

# # emails = delivery['email']
# # emails = emails.drop_duplicates()
# # emails.count()