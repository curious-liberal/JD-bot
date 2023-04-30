# JD bot

## Description

### Main features

This project includes a module that allows you to:
 + Login to a JD account using Python requests
 + Import/ Export previous sessions
 + Extract specific information about shoes
 + Add a shoe to your cart (with specified shoe-size)

### Plans for future

In future plans include:
 + A GUI interface
 + Purchasing of shoe
 + Cancelling of purchases
 + Receiving verification codes
 + Secure, remote access via Discord bot

# Basic usage

To start, ensure the "request_bot" python file is the your working directory

Next import the module to unlock THE POWER!!!

```
import request_bot
```

If you wish to login to your JD account insert the following code 

```
login_details = request_bot.get_creds()
```

It is also advisable to store the URL for the shoe you wish to use in a variable

```
shoe = "https://www.url.to.jd.shoe.com/blah-blah-blah"
```

To create the bot instantiate the "Beanjuice" object

```
bot = Beanjuice()
```

It strongly recommended to add the following instance attributes according to your needs:

+ Credentials - feel free to use: ```credentials=login_details``` OR ```credentials=["username", "password"]```
+ Shoe URL: - ```shoe_url```
+ Console output: ```True``` or ```False```
