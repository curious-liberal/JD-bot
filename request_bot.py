"""
Module with bot that can easily login
to JD and automatically buy products
"""
from getpass import getpass
from time import sleep
import pickle
import re
from bs4 import BeautifulSoup as bs
import requests


def get_creds():
    """
    Asks user for username and password
    via console, password is obscured
    """
    print("Please enter your JD login credentials below\n")
    username = str(input("Email/ Username: "))
    password = getpass("Password: ")

    return [username, password]

def log(stuff, output):
    """prints to console,
    can be silent
    """
    if output is True:
        print(stuff)

class Beanjuice:
    """main class that is able to
    run the majority of the functions
    """
    def __init__(self, shoe_url=None,
    credentials=[None, None],
    console_output=True,
    proxy_file=None,
    headers_file=None,
    cookies_file=None):

        # URL for shoe to buy + login credentials
        self.shoe = shoe_url

        # Payload for logging in
        self.login_payload = {"username": credentials[0],
        "password": credentials[1],
        "cartMerge":"true"}

        # Whether to print to console or not
        self.output = console_output

        # Setting proxy, cookies & header files
        self.proxy_file = proxy_file
        self.headers_file = headers_file
        self.cookies_file = cookies_file

    def switch_proxy(self):
        """Amazing function which reads from a list of proxies
        in a text file where each line is a new proxy. Will then set that as the
        proxy to make requests with. Best part is that it automatically cycles through
        the proxies by moving the chosen proxy to the end of the list and picking the first
        proxy on the list each time
        """
        try:
            with open(self.proxy_file, "r") as proxy_list:
                proxies = proxy_list.read().splitlines()
                # Pick proxy from start of list
                global default_proxy
                default_proxy = {"https": proxies[0]}

                # Move proxy to bottom of list
                proxies.remove(default_proxy["https"])
                proxies.insert(len(proxies), default_proxy["https"])

                # Write the newly ordered proxy list to the file
                with open(self.proxy_file, "w") as proxy_list_new:
                    proxy_list_new.write("\n".join(proxies))

        except (FileNotFoundError, TypeError):
            log(f"Proxy file '{self.proxy_file}' doesn't exist, so you are NOT USING proxies",
            self.output)
            self.proxy_file = None

    def set_proxy(self, sesh):
        """Set proxy for session
        with checks in place to see if a
        proxy and proxy file have been established
        """
        try:
            if self.proxy_file is not None:
                sesh.proxies = default_proxy
        except NameError:
            log("Must call 'switch_proxies' first, no proxies are in use", self.output)

    def switch_headers(self):
        try:
            with open(self.headers_file, "r") as header_list:
                headers = header_list.read().splitlines()
                # Pick header from start of list
                global default_headers
                default_headers = {"user-agent": headers[0], "accept": "*/*"}

                # Move header to bottom of list
                headers.remove(default_headers["user-agent"])
                headers.insert(len(headers), default_headers["user-agent"])

                # Write the newly ordered header list to the file
                with open(self.headers_file, "w") as header_list_new:
                    header_list_new.write("\n".join(headers))

        except (FileNotFoundError, TypeError):
            log(f"Header file '{self.headers_file}' doesn't exist, so you are NOT USING headers",
            self.output)
            self.headers_file = None

    def set_headers(self, sesh):
        """Set headers for session
        with checks in place to see if a
        header and header file have been established
        """
        try:
            if self.headers_file is not None:
                sesh.headers = default_headers
        except NameError:
            log("Must call 'switch_headers' first, no headers are in use", self.output)

    def load_cookies(self, sesh):
        """loads cookies from
        last session"""
        try:
            log("Attempting to import cookies...", self.output)
            with open(self.cookies_file, "rb") as cookiejar:
                sesh.cookies.update(pickle.load(cookiejar))
        except FileNotFoundError:
            log("Cookies not created yet, will save new cookies at end of session", output=True)

    def save_cookies(self, sesh):
        """saves/ exports cookies from session
        if cookie file has been set
        """
        if self.cookies_file is not None:
            with open(self.cookies_file, "wb") as cookiedata:
                pickle.dump(sesh.cookies, cookiedata)
                log(f"Saved cookies under file name '{self.cookies_file}'", self.output)

    def login(self, import_login=False):
        """logs into JD accout, ready to purchase items
        """
        with requests.Session() as sess:
            # Setting headers and proxies if they've been established
            self.set_headers(sess)
            self.set_proxy(sess)

            # Login when performing this request (if specified)
            if import_login is True:
                self.load_cookies(sess)
            else:
                log("Logging into JD....", self.output)
                signin = requests.post("https://www.jdsports.co.uk/myaccount/login/",
                json=self.login_payload, timeout=10)

                # Output JSON error msg if not recieved code 200 (OK)
                if signin.status_code == 200:
                    log(f"Sign-in successful, redirected to: {signin.url} with status \
                    {signin.status_code}", self.output)
                    sleep(2)

            log("Connecting to jdsports.co.uk...", self.output)
            requests.get("https://www.jdsports.co.uk", timeout=10)
            log("Connection successful", self.output)
            sleep(2)

            log("Connecting to JD Dashboard", self.output)
            requests.get("https://www.jdsports.co.uk/myaccount/dashboard/", timeout=10)
            sleep(1)

            self.save_cookies(sess)

    def get_shoe_info(self, import_login=False):
        """Returns dictionary containing name, price and
        available shoe when sizes given URL of shoe
        """
        with requests.Session() as sess:
            # Setting headers and proxies if they've been established
            self.set_headers(sess)
            self.set_proxy(sess)

            # Login when performing this request (if specified)
            if import_login is True:
                self.load_cookies(sess)

            shoe = sess.get(f"{self.shoe}/stock", timeout=10)

            # Log to console if not response 200 (OK)
            if shoe.status_code != 200:
                log(f"Error, couldn't reach {self.shoe}",
                self.output)

        # Extract info
        soup = bs(shoe.text, "lxml")

        # Takes shoe name from URL
        shoe_name = re.search(r"product/(.*?)/\d{3,}", self.shoe).group(1)

        # Find price from variable in HTML button
        shoe_price = soup.find("button", {"data-e2e": "pdp-productDetails-size"})["data-price"]

        # Shoe sizes
        sizes_raw = soup.find_all("button", {"data-e2e": "pdp-productDetails-size"})
        available_sizes = []

        for size in sizes_raw:
            # Display digit in string, if a dot and another digit \
            # is immediately present, display those too
            size_clean = re.findall(r"\d+\.?\d?", size.text)[0]
            available_sizes.append(size_clean)

        # Return data
        return {"name": shoe_name,
        "price": shoe_price,
        "available-sizes": available_sizes
        }

    def add_to_cart(self, shoe_size):
        """Add self.shoe to cart ready for purchase
        """
        with requests.Session() as sess:
            # Setting headers and proxies if they've been established
            self.set_headers(sess)
            self.set_proxy(sess)

            # Try to previous sessions cookies
            self.load_cookies(sess)

            shoe = sess.get(f"{self.shoe}", timeout=10)

            # Log to console if not response 200 (OK)
            if shoe.status_code != 200:
                log(f"Error, couldn't reach {self.shoe}",
                self.output)

            # Extract "data-sku" (a weird ID needed to add product to cart)
            shoe_raw = shoe.text
            shoe_size_name = re.findall(r"name:\"(.*?)\"", shoe_raw)
            shoe_id = re.findall(r"page_id_variant: \"(.*?)\"", shoe_raw)

            # Create dictionary of shoe2data-sku
            data_sku = dict(zip(shoe_size_name, shoe_id))

            # Cart payload (data to send off)
            cart_payload = {"customisations": None,
            "cartPosition": None,
            "recaptchaResponse": None,
            "cartProductNotification": None,
            "quantityToAdd": 1,
            "invalidateCache": True}

            # Make request to add to cart
            cart_req = requests.post(f"https://www.jdsports.co.uk/cart/{data_sku[shoe_size]}",
            json=cart_payload, timeout=10)

            # Check if item was added to cart correctly
            if cart_req.status_code == 200:
                log(r"Added to cart successfully \o/", self.output)
            else:
                log("Add to cart request failed :(", self.output)
