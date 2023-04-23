"""
Bot to login to JD account using requests
"""
from request_bot import get_creds, Beanjuice

# Asks user for login details
login_details = get_creds()

# Shoe to buy
shoe = "https://www.jdsports.co.uk/product/grey-nike-air-max-95-ultra/19457267/"

# Creates bot
bot = Beanjuice(credentials=login_details,
shoe_url=shoe, headers_file="headers.txt",
cookies_file="cookies.pkl",
proxy_file="proxies.txt")

bot.switch_proxy()

# Logs in with recently inputted login credentials
bot.login()

# Provides information about the shoe inputted
print(bot.get_shoe_info(import_login="True"))

bot.add_to_cart("7")
