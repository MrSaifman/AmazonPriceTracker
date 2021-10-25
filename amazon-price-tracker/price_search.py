import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent


class PriceSearch:
    def get_headers(self):
        user_agent = generate_user_agent()
        head = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
        }
        return head

    def lookup(self, url: str):
        url = url.lower()
        if url[0:23] != "https://www.amazon.com/" and url[0:15] != "www.amazon.com/":
            return (False, "INVALID: Needs to be an Amazon product URL!")

        try:
            headers = self.get_headers()
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
        except Exception:
            return (False, "INVALID: Page does not exist!")

        webpage = response.text
        soup = BeautifulSoup(webpage, "html.parser")
        return (True, soup)

    def lookup_product(self, url: str):
        soup = self.lookup(url)
        if soup[0] is False:
            return soup
        else:
            soup = soup[1]

        try:
            product_price = soup.find(
                name="span",
                id=lambda x: x and x.startswith('priceblock_')
                ).get_text()[1:]
            if '-' in product_price:
                return (False, "INVALID PAGE: Please select size/product of the item your interested in!")
            product_name = soup.find(
                name="span",
                id="productTitle").get_text().replace('\n', '')
        except Exception:
            return (False, "INVALID PAGE: Please provide url of a product page!")

        try:
            img_url = soup.find(name="img", alt=product_name)['src']
        except Exception:
            try:
                img_url = soup.find(name="img", class_="a-dynamic-image")['src']
            except Exception:
                return (False, "IMAGE ERROR: Please Contact Developer!")

        return (True, product_price, product_name, img_url)

    def lookup_price(self, url):
        soup = self.lookup(url)
        if soup[0] is False:
            return soup
        else:
            soup = soup[1]

        try:
            product_price = soup.find(
                name="span",
                id=lambda x: x and x.startswith('priceblock_')
                ).get_text()[1:]
            if '-' in product_price:
                return (False, "INVALID PAGE: Please select size/product of the item your interested in!")
        except Exception:
            return (False, "INVALID PAGE: Please provide url of a product page!")

        return (True, product_price)
