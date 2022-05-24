# Functions that manipulate the selenium driver object for web scraping

# Logger Setup
import logging
from logging.config import fileConfig
fileConfig('./logging_config.ini')
logger = logging.getLogger('fire')



# Imports specific to this set of functions
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os.path
import time
import datetime
from dotenv import load_dotenv
import pytz

#get .env file from current directory
cwd = os.getcwd()
load_dotenv(cwd + '/vars.env')

fire_creds = os.getenv('FIREBASE_CREDS')


# Use a service account

cred_dict = {
    "type": "service_account",
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-g2gtq%40southernhobby-1609270303994.iam.gserviceaccount.com"
}
f_cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(f_cred)
db = firestore.client()


#read from DB
def read_orders_from_firestore(start = '01/01/1900',end = '12/31/2100'):
    """
    returns a dict with a specified collection
    """
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%m/%d/%Y')
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%m/%d/%Y')

    docs = db.collection(u'Orders').where(u'date', u'>=',start).where(u'date', u'<=',end).stream()

    # doc_ref = db.collection(collection)
    # docs = doc_ref.stream()

    temp_dict = {}

    # TODO write a function to compare the "orders" screen to the "order details" screen. That will help if the display error happens on the order details screen.

    for doc in docs:
        temp_dict[doc.id] = doc.to_dict()
        # print(f'{doc.id} => {doc.to_dict()}')
    return temp_dict

def read_items_from_firestore(start , end):
    """
    returns a dict of items based on a list of fields and corresponding criteria

    conditions dict has 3 keys: 'field','operator','criteria'
    ex: 
        field = 'date'
        operator = '<='
        criteria = '4/15/2021'
    """
    print('read from firestore')
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%m/%d/%Y')
        print(start.isoformat())
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%m/%d/%Y')
        end = end.replace(hour=23,minute=59,second=59)
        print(end.isoformat())

    if start == end:
        end.replace

    cookie_categories = [
        'Round',
        'Shapes',
        'Custom',
        'Open Cake',
        'Frequent Shapes',
        'Spring Holiday Shapes',
        'Numbers',
        'Sports',
        'Summer Holiday Shapes',
        'Winter Holiday Shapes',
        'Fall Holiday Shapes']

    # FIXME - excessive reads per database pull, see if this can be limited
    orders_ref = db.collection(u'Orders').where(u'date', u'>=',start).where(u'date', u'<=',end).stream()

    order_list = []

    for order in orders_ref:
        # print(order.id)
        order_list.append(order.id)

    if len(order_list) == 0:
        return {'donut_list': [], 'cookie_list': []}
    else:
        print('len of list of orders: ', len(order_list))
    

        donut_list = []
        cookie_list = []

        docs = db.collection(u'Items').stream()

        for doc in docs:
            temp_dict = doc.to_dict()
            # print('eval data: ', temp_dict)
            if temp_dict['order_id'] in order_list and temp_dict['category'] == 'Donuts':
                # print('match: ', temp_dict['order_id'])
                if temp_dict['voided'] == 'false':
                    donut_list.append(temp_dict)
                    # print(temp_dict)
            if temp_dict['order_id'] in order_list and temp_dict['category'] in cookie_categories:
                # print('match: ', temp_dict['order_id'])
                if temp_dict['voided'] == 'false':
                    cookie_list.append(temp_dict)
                    
        return {'donut_list':donut_list, 'cookie_list':cookie_list}

def add_orders_from_dict(orders_dict):
    """
        send a dict (made from a dataframe) for upload to firestore. One new document per line
    """
    
    timezone = pytz.timezone('America/Chicago')
    dates = {'min':datetime.datetime(2100,1,1,0,0,0,0,timezone),'max':datetime.datetime(1900,1,1,0,0,0,0,timezone)}
    

    # TODO handle nan values prior to this steps
    # print('received dict: ', orders_dict)
    for i in orders_dict.values(): 
        #rework the structure of the dict. Order_id = key, else = value
        i['date'] = datetime.datetime.strptime(i['date'], '%m/%d/%Y')
        i['date'] = timezone.localize(i['date'])
        order_id = i['order_id']
        data = {
            'date': i['date'],
            'time': i['time'],
            'email': i['email'],
            'name': i['name'],
            'order_friendly_id': i['order_friendly_id'],
            'order_type': i['order_type'],
            'address': i['address'],
            'delivery_instructions' :i['delivery_instructions'],
            'phone': i['phone'],
        }

        # push to firebase
        db.collection(u'Orders').document(order_id).set(data)

        if i['date'] < dates['min']:
            dates['min'] = i['date']
        if i['date'] > dates['max']:
            dates['max'] = i['date']
    
    return 'Yes'

def gen_item_key(d):
    '''
    Generates a unique key for an item to prevent duplicates when uploading
    '''
    # last 4 digits of the order_id
    le = len(d['order_id'])
    a = d['order_id'][le-8:le]

    # item key iterator
    b = d['item_key']

    # first 3 letters of category
    c = d['category'][:3]

    if any(substring in d['item_name'] for substring in ['/','*']):
        item = d['item_name'].replace('/','Z')
        item = item.replace('*','Z')
        e = item[:3]
    else: 
        e = d['item_name'][:3]

    f = d['qty']
    
    item_key = a + '-' + str(b) + '-' + c + e + str(f)
    
    return item_key

def add_exception(e):
    '''
    takes a dict containing exception info 
    '''
    db.collection(u'Exceptions').document().set(e)

def add_items_from_dict(items_dict):
    for i in items_dict.values(): 
        item_key = gen_item_key(i)
        # print(i.get('order_id'))
        data = {
            'order_id' : i.get('order_id'),
            'order_friendly_id'  : i.get('order_friendly_id'),
            'item_name'  : i.get('item_name'),
            'category'  : i.get('category'),
            'voided'  : i.get('voided'),
            'wrapping'  : i.get('wrapping'),
            'bg_color'  : i.get('bg_color'),
            'sprinkles'  : i.get('sprinkles'),
            'other_requests'  : i.get('other_requests'),
            'qty' : i.get('qty')
        }
        # print(item_key)
        db.collection(u'Items').document(item_key).set(data)

def set_categories(cats:list):
    """
        Adds new categories in firebase
        List of dicts format:
            {item_name: string, category: string}
    """
    logger.debug('set_categories')
    for cat in cats:
        data = {
            'item_name': cat['item_name'],
            'category': cat['category']
        }
        logger.debug(f'data: {data}')
        db.collection(u'Categories').document().set(data)

def get_categories():
    """
        Retrieves the entire categories collection from firebase
    """
    logger.debug('get_categories_from_firebase')
    cats = db.collection(u'Categories').stream()
    temp = []

    for cat in cats:
        temp.append(cat.to_dict())

    return temp 

def delete_voided_orders_and_items(order_ids):
    batch = db.batch()

    for oid in order_ids:
        print('oid: ',oid)
        batch.delete(db.collection(u'Orders').document(oid))

        docs = db.collection(u'Items').where(u'order_id',u'==',oid).stream()
        for doc in docs:
            # print('doc:', doc)
            batch.delete(doc.reference)
    
    batch.commit()
            
