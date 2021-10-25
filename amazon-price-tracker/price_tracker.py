import json
from datetime import datetime
from price_search import PriceSearch
from data_manager import DataManager

dataMnger = DataManager()
priceSrch = PriceSearch()


def check_price():
    data = dataMnger.get_urls()
    ids = data[0]
    urls = data[1]

    for i in range(0, len(ids)):
        price = priceSrch.lookup_price(urls[i])
        if price[0] is True:
            price = price[1]
            dataMnger.update_product_db(ids[i], price)
        else:
            return False
    return True


def update_check_date():
    time = datetime.now().strftime('%Y-%m-%d\n%I:%M %p')

    with open('config.json') as file:
        data = json.load(file)
        data['last_check'] = time

    with open('config.json', 'w') as file:
        # file.seek(0)
        file.write(json.dumps(data, indent=4))
    return time


def read_check_date():
    with open('config.json') as file:
        data = json.load(file)
        return data['last_check']
