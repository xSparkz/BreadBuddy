# URL's
URL_LOGIN = 'https://orders.westonfoods.ca/edistributor/'

# Regular Expressions
REGEX_ORDER_STORENAME = '<span id="ctl00_main_ucCustomerOrder_lblCustInfoLeft" style="font-size:14px;font-weight:bold;">([\\s\\S]*?)<\\/span>' # FOOD BASICS<br/>1300050287 - FOOD BASICS CORPORATE # 58872
REGEX_ORDER_STOREADDRESS = '<span id="ctl00_main_ucCustomerOrder_lblCustInfoRight" style="font-size:14px;font-weight:bold;">([\\s\\S]*?)<\\/span>' # 199 SIMCOE ST<br/>KESWICK, ON, L4P 2H6

def Echo(lineToEcho):

    print lineToEcho