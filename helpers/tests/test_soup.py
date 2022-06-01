import datetime
from unittest import mock
import pytest
import pytest_mock

from helpers.soup import extract_orders_from_order_details

@pytest.fixture
def soup_list():
    _html_list = []
    with open('helpers/tests/valid_order_details.html','r') as file:
        _html_list.append(file.read())
    return _html_list

@pytest.mark.single
def test_extract_orders_from_order_details(soup_list):
    df = extract_orders_from_order_details(soup_list)

    expected = ['order_id', 'order_friendly_id', 'order_status', 'item_name', 'qty',
       'unit_price', 'discount', 'net_price', 'taxes', 'total_price', 'reason',
       'refund_qty', 'refund_amt', 'mods', 'customer', 'datetime', 'voided']

    assert df.size == 51
    assert len(df.columns) == len(expected) 
    assert all([a == b for a,b in zip(df.columns,expected)])
    assert df[df['order_id']== '500000017401140395']['qty'] == 2000 #test for commas in strings