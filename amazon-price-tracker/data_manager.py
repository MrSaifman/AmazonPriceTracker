from datetime import datetime
from utils import Utils
import pandas as pd
import os


class DataManager:
    def __init__(self):
        self.utility = Utils()

    def add_item(self, product_name: str, price: float, desired_price: float, url: str):
        data = self.fetch_database()
        if data is None:
            columns = [
                'id',
                'product_name',
                'recent_price',
                'desired_price',
                'checked_date',
                'url']
            data = pd.DataFrame(columns=columns)

        date = datetime.now().date()
        id = self.utility.encode(url)
        product = data.loc[data['url'] == url]

        if product.empty:
            series_data = {
                'id': id,
                'product_name': product_name,
                'recent_price': price,
                'desired_price': desired_price,
                'checked_date': date,
                'url': url}

            data = data.append(series_data, ignore_index=True)
            self.create_product_db(id)
        else:
            data.loc[data['url'] == url, :] = [
                id,
                product_name,
                price,
                desired_price,
                date,
                url]

        self.update_product_db(id, price)

        data.to_csv('databases/tracking_database.csv',  index=False)

    def remove_item(self, product_name=None, url=None):
        data = self.fetch_database()
        if data is None:
            return

        if product_name is not None:
            try:
                product = data.loc[data["product_name"] == product_name]
                id = product['id'].values[0]
                product_index = product.index

                if product_index.size == 0:
                    print(f"{product_name} not found in database.")
                    return

                data = data.drop(product_index)
                os.remove(f'databases/product_databases/{id}.csv')
            except KeyError:
                print(f"{product_name} not found in database.")
                return
        elif url is not None:
            try:
                product_index = data.loc[data["url"] == url].index
                if product_index.size == 0:
                    print(f"{url} not found in database.")
                    return
                data = data.drop(product_index)
            except KeyError:
                print(f"{product_name} not found in database.")
                return
        else:
            pass

        data.to_csv('databases/tracking_database.csv', index=False)

    def create_product_db(self, id):
        columns = ['date', 'price']
        data = pd.DataFrame(columns=columns)
        data.to_csv(f'databases/product_databases/{id}.csv', index=False)

    def update_product_db(self, id, price):
        try:
            data = pd.read_csv(f'databases/product_databases/{id}.csv')
        except FileNotFoundError:
            print(f"{id} file not found in product_databases.")
            return

        date = datetime.now().date()
        date_index = data.loc[data["date"] == str(date)].index

        if date_index.size == 0:
            series_data = {
                'date': date,
                'price': price}
            data = data.append(series_data, ignore_index=True)
        else:
            data.loc[data['date'] == date, :] = [date, price]

        data.to_csv(f'databases/product_databases/{id}.csv', index=False)

    def get_items(self):
        data = self.fetch_database()
        items = data['product_name'].to_list()
        return items

    def get_product_data(self, product_name: str):
        data = self.fetch_database()
        if data is None:
            return

        id = data.loc[data['product_name'] == product_name, :]['id'].values[0]
        product_row = data.loc[data['product_name'] == product_name, :]
        desired_price = product_row['desired_price'].values[0]

        product_data = pd.read_csv(f'databases/product_databases/{id}.csv')
        dates = product_data['date'].to_list()
        prices = product_data['price'].to_list()
        return (dates, prices, desired_price)

    def get_price_data(self, product_name: str):
        try:
            data = pd.read_csv('databases/tracking_database.csv')
            product_row = data.loc[data['product_name'] == product_name, :]
            id = product_row['id'].values[0]
            desired_price = product_row['desired_price'].values[0]

            product_data = pd.read_csv(f'databases/product_databases/{id}.csv')
            dates = product_data['date'].to_list()
            prices = product_data['price'].to_list()

            current_price = prices[-1]
            current_date = dates[-1]

            highest_price = prices[0]
            lowest_price = prices[0]

            for price in prices:
                if price > highest_price:
                    highest_price = price

                if price < lowest_price:
                    lowest_price = price

            lowest_date = product_data.loc[product_data['price'] == lowest_price, :]['date'].values[-1]
            highest_date = product_data.loc[product_data['price'] == highest_price, :]['date'].values[-1]

            desired_price = "{:.2f}".format(desired_price)
            current_price = "{:.2f}".format(current_price)
            lowest_price = "{:.2f}".format(lowest_price)
            highest_price = "{:.2f}".format(highest_price)

            price_data = {
                "desired_price": desired_price,
                "current_price": current_price,
                "current_date": current_date,
                "lowest_price": lowest_price,
                "lowest_date": lowest_date,
                "highest_price": highest_price,
                "highest_date": highest_date
            }

            return price_data
        except FileNotFoundError:
            print("tracking_database file not found.")
            return

    def update_watchprice(self, product_name, updated_price):
        data = data = self.fetch_database()
        if data is None:
            return
        data.loc[data[
            'product_name'] == product_name,
            ["desired_price"]] = [updated_price]
        data.to_csv('databases/tracking_database.csv',  index=False)
        return

    def get_urls(self):
        data = self.fetch_database()
        urls = data['url'].to_list()
        ids = data['id'].to_list()

        return (ids, urls)

    def fetch_database(self):
        try:
            return pd.read_csv('databases/tracking_database.csv')
        except FileNotFoundError:
            print("tracking_database file not found.")
            return
