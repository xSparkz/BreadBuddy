__author__ = 'xSp4rkz'

# This file is part of Bread Buddy.

# Bread Buddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Police Dash Pad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Bread Buddy.  If not, see <http://www.gnu.org/licenses/>.

import mechanize, cookielib, re
from bs4 import BeautifulSoup
from common import Echo
from settings import *

LINK_BASE_URL = 'https://orders.westonfoods.ca/'
LINK_BASE_ORDERS = LINK_BASE_URL + 'eDistributor/Secure/Distributor/'
LINK_LOGIN = 'https://orders.westonfoods.ca/eDistributor/Login.aspx'

class WebsiteConnection():

    def __init__(self, UserName, Password):

        #Authentication
        self.__LoggedIn = False

        self.__Username = UserName
        self.__Password = Password

        #Browser
        self.__Browser = mechanize.Browser()

        #Cookie Jar
        self.__CookieJar = cookielib.LWPCookieJar()
        self.__Browser.set_cookiejar(self.__CookieJar)

        #Browser Options
        self.__Browser.set_handle_equiv(True)
        self.__Browser.set_handle_redirect(True)
        self.__Browser.set_handle_referer(True)
        self.__Browser.set_handle_robots(False)

        self.__Browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        #Site Map
        self.__Random_Customer_URL = None

        #Properties
        self.__RouteNumber = None
        self.__RouteOwner = None


    def RouteNumber(self): return self.__RouteNumber

    @staticmethod
    def DayOfTheWeek(StringToParse):

        if 'Day1Cell' in StringToParse: return 'Sunday'
        if 'Day2Cell' in StringToParse: return 'Monday'
        if 'Day3Cell' in StringToParse: return 'Tuesday'
        if 'Day4Cell' in StringToParse: return 'Wednesday'
        if 'Day5Cell' in StringToParse: return 'Thursday'
        if 'Day6Cell' in StringToParse: return 'Friday'
        if 'Day7Cell' in StringToParse: return 'Saturday'

    def __GetRouteInfo(self, SourceCode):

        #Prepare the data
        HTML = BeautifulSoup(SourceCode)

        #Get route number
        RouteInfo = HTML.find('span', attrs={'id':'ctl00_main_RouteDashboard1_ucNormalOrderLoadVolume_lblLoadVolumeInfoLeft'})

        if RouteInfo is not None:

            RouteInfo = str(RouteInfo.text).replace('Route Summary ViewRoute: ','')
            RouteInfo = RouteInfo.split(',')

            if len(RouteInfo) > 1:

                self.__RouteNumber = str(RouteInfo[0]).strip()
                self.__RouteOwner = str(RouteInfo[1].strip())

        return


    def Login(self):

        #Safety check
        if not self.__CheckCredentials(): return

        #Connect
        Echo('Connecting to website')
        self.__Browser.open(LINK_LOGIN)

        Response = self.__Browser.response()
        ResponseCode = Response.code
        SourceCode = Response.read()

        if not ResponseCode == 200:

            Echo('Uh Oh! Something happened. Not sure what.')
            Echo(('\t- Received response: ' + ResponseCode + ' from server'))
            Echo('\t - Login failed!')

            return False

        #Login
        Echo('Logging in...')

        self.__Browser.select_form("aspnetForm")
        self.__Browser['ctl00$main$txtUserName'] = self.__Username
        self.__Browser['ctl00$main$txtPassword'] = self.__Password
        self.__Browser.method = "POST"

        Echo(('\t- Set username: ' + self.__Username))

        if OPTION_HIDE_PASSWORDS:

            Echo(('\t- Set password: ' + self.__MaskPassword(self.__Password)))

        else:

            Echo(('\t- Set password: ' + self.__Password))

        Response = self.__Browser.submit()
        ResponseCode = Response.code
        SourceCode = Response.read()

        Echo('\t- Checking response')
        Echo(('\t- Response code: ' + str(ResponseCode)))
        if ResponseCode == 200: Echo('\t- OK!')
        Echo('\t- Extracting data')

        #Get route number and owner name and store it
        self.__GetRouteInfo(SourceCode)

        #Time to scan the links to find a random customer. Once we find a random customer we can view their order
        #and map out the remaining list of customers which will be accessible via a customers order page by scanning the side menu

        FoundRandomCustomer = False

        #Link(base_url='https://orders.westonfoods.ca/eDistributor/Secure/Distributor/IDDashboard.aspx?rid=206255&sid=2&date=2014-11-21&Digest=aVVgQFhR6qWnMllD+oVIYA', url="javascript:__doPostBack('ctl00$main$RouteDashboard1$ucNormalOrderDetailHistory$grdNormalOrderHistoryDashboardResults$ctl33$lnkBtnViewOrder','')", text='View Order', tag='a', attrs=[('onclick', "RedirectWindow('/eDistributor/Secure/Distributor/CustomerOrderView.aspx?cid=1895023452&sid=2&date=2014-11-18&Digest=KZx2eDVQKqI2QyKRRwttUQ');  return false;"), ('id', 'ctl00_main_RouteDashboard1_ucNormalOrderDetailHistory_grdNormalOrderHistoryDashboardResults_ctl33_lnkBtnViewOrder'), ('href', "javascript:__doPostBack('ctl00$main$RouteDashboard1$ucNormalOrderDetailHistory$grdNormalOrderHistoryDashboardResults$ctl33$lnkBtnViewOrder','')")])
        for Link in self.__Browser.links():

            if FoundRandomCustomer: break #Stop searching if we found a random customer already

            if hasattr(Link, 'text') and hasattr(Link, 'attrs'):

                if Link.text == 'View Order':

                    #[('onclick', "RedirectWindow('/eDistributor/Secure/Distributor/CustomerOrderView.aspx?cid=1895023452&sid=2&date=2014-11-18&Digest=KZx2eDVQKqI2QyKRRwttUQ');  return false;"), ('id', 'ctl00_main_RouteDashboard1_ucNormalOrderDetailHistory_grdNormalOrderHistoryDashboardResults_ctl33_lnkBtnViewOrder'), ('href', "javascript:__doPostBack('ctl00$main$RouteDashboard1$ucNormalOrderDetailHistory$grdNormalOrderHistoryDashboardResults$ctl33$lnkBtnViewOrder','')")]
                    for TagValues in Link.attrs:

                        if FoundRandomCustomer: break #Stop searching if we found a random customer already

                        #'onclick'
                        #"RedirectWindow('/eDistributor/Secure/Distributor/CustomerOrderView.aspx?cid=1895023452&sid=2&date=2014-11-18&Digest=KZx2eDVQKqI2QyKRRwttUQ');  return false;")'
                        Tag, Value = TagValues

                        if 'CustomerOrderView.aspx?' in Value:

                            #Found a link to a customer's order. Visiting it will lead to more customers to discover..
                            #Store the link, but strip away the garbage and reconstruct it.
                            CustomerURL = str(Value)
                            CustomerURL = CustomerURL.replace('RedirectWindow(\'','')
                            CustomerURL = CustomerURL.replace('\');  return false;','')

                            CustomerURL = LINK_BASE_URL + CustomerURL #Glue it all together

                            self.__Random_Customer_URL = CustomerURL #Store it

                            FoundRandomCustomer = True #No need to keep searching. Tell the others. lol

                            break

        if FoundRandomCustomer:

            Echo('\t- Success!')
            Echo('\t- Done!')

            Echo('Logged in as: ' + self.__Username)
            if self.RouteNumber() is not None: Echo(('\t- Route #: ' + self.RouteNumber()))
            Echo('\t- Done!')

            return True

        Echo('\t- Received unexpected response. Aborting..')
        Echo('Login failed!')

        return False


    def FetchCustomers(self):

        #Safety checks
        if not self.__CheckCredentials(): return None

        if self.__Random_Customer_URL is None:

            Echo('Cannot fetch customers. Not logged in..')
            return None

        #Fetch customers
        Echo('Fetching customers..')
        self.__Browser.open(self.__Random_Customer_URL)

        Response = self.__Browser.response()
        ResponseCode = Response.code
        SourceCode = Response.read()

        Echo('\t- Checking response')
        Echo('\t- Response code: ' + str(ResponseCode))
        if ResponseCode == 200: Echo('\t- OK!')

        #Prepare the data
        Echo('\t- Reading source code')

        HTML = BeautifulSoup(SourceCode)

        Echo('\t- Done!')


        Echo('Scanning for customer links')
        Links = HTML.findAll('a')
        CustomerInfo = []
        BulkOrderURL = ''

        Blacklist = {'ctl00_main_ucCustomerOrder_lnkLastWeek1', 'ctl00_main_ucCustomerOrder_lnkNextWeek2'}

        for Link in Links:

            try:

                if not Link.attrs['id'] in Blacklist: #To ignore or not to ignore. That is the question.

                    if 'CustomerOrderView.aspx?' in Link.attrs['href']:

                        Customer = str(Link.text).rsplit('#',1)
                        CustomerName = Customer[0].strip()
                        CustomerAccountNumber = Customer[1].strip()
                        CustomerURL = str(LINK_BASE_ORDERS + Link.attrs['href'])

                        CustomerInfo.append((CustomerName, CustomerAccountNumber, CustomerURL))

                    if 'BulkOrderView.aspx?' in Link.attrs['href']:

                        BulkOrderURL = str(LINK_BASE_ORDERS + Link.attrs['href'])

            except: pass

        Echo(('\t- Found ' + str(len(CustomerInfo)) + ' customer(s)'))
        Echo('\t- Done!')

        return CustomerInfo

    def FetchOrder(self, Customer):

        #Safety checks
        if not self.__CheckCredentials(): return None
        if Customer is None: return None

        Echo(('Fetching order for: ' + Customer[0] + ' - ' + str(Customer[1])))

        self.__Browser.open(Customer[2])

        Response = self.__Browser.response()
        ResponseCode = Response.code
        SourceCode = Response.read()

        Echo('\t- Checking response')
        Echo(('\t- Response code: ' + str(ResponseCode)))
        if ResponseCode == 200: Echo('\t- OK!')

        #Prepare the data
        Echo('\t- Reading response')
        HTML = BeautifulSoup(SourceCode)
        Echo('\t- Examining order..')

        #Find product codes
        #(a) ctl00_main_ucCustomerOrder_lstProducts_ctrl0_hidProductId
        RegEx = {}
        RegEx['ProductID'] = 'ctl.+(_main_ucCustomerOrder_lstProducts_ctrl).+(_hidProductId)'

        Products = HTML.findAll('input',  {'id' : re.compile(RegEx['ProductID'])})

        #Orders will contain all products for the entire week separated into lists for each day
        #Orders list will contain Order list
        #Layer (1) Day of Week, Product Code, Product Name, Temp Order, Perm Order
        Orders = []

        if Products is not None:

            Echo('\t\t- Checking product codes..')

            for Product in Products:

                if Product.has_attr('value'):

                    #Initiate variables
                    ProductCode = ''
                    ProductDescription = ''
                    TotalTemp = 0
                    TotalPerm = 0

                    #Extract product code
                    ProductCode = str(Product.attrs['value']).lstrip('0')

                    #Find product description
                    #(a) ctl00_main_ucCustomerOrder_lstProducts_ctrl0_hidProductId
                    #(b) ctl00_main_ucCustomerOrder_lstProducts
                    TempString = str(Product.attrs['id']).rsplit('_', 1)

                    if len(TempString) > 1:

                        HeaderTag = TempString[0]

                        #(a) ctl00_main_ucCustomerOrder_lstProducts_ctrl0
                        #(b) _lblProductName
                        #(c) ctl00_main_ucCustomerOrder_lstProducts_ctrl0_lblProductName
                        RegEx['ProductName'] = HeaderTag + '(_lblProductName)'
                        ProductDescription = HTML.find('span',  {'id' : re.compile(RegEx['ProductName'])})

                        #Extract product name
                        if ProductDescription is not None:

                            #01961 - FS 4" PLAIN HAM 12'S - 6 / Tray
                            ProductName = str(ProductDescription.text).split('-', 1)

                            ProductName = str(ProductName[1]).rsplit('-', 1)

                            TrayCount = str(ProductName[1]).split('/', 1)

                            ProductName = str(ProductName[0]).strip()

                            TrayCount = int(str(TrayCount[0]).strip())

                        #(a) ctl00_main_ucCustomerOrder_lstProducts_ctrl0
                        #(b) _txtL or _txtR
                        #(c) ctl00_main_ucCustomerOrder_lstProducts_ctrl0_ucDay1Cell_txtL
                        RegEx['TempOrder'] = HeaderTag + '_.+(Cell_txtL)' #Temp orders #TODO Sloppy - Re-code
                        RegEx['PermOrder'] = HeaderTag + '_.+(Cell_txtR)' #Permanent orders
                        TempOrders = HTML.find_all('input', {'id' : re.compile(RegEx['TempOrder'])})
                        PermOrders = HTML.find_all('input', {'id' : re.compile(RegEx['PermOrder'])})

                        #Temp orders
                        for TempOrder, PermOrder in zip(TempOrders, PermOrders):

                            if TempOrder.has_attr('value') and PermOrder.has_attr('value'):

                                id = str(TempOrder.attrs['id'])

                                Orders.append((self.DayOfTheWeek(id),
                                               ProductCode,
                                               ProductName,
                                               TempOrder.attrs['value'],
                                               PermOrder.attrs['value'],
                                               TrayCount))
            Echo('\t\t- Finished!')

            if len(Orders) > 1:

                return Orders

            else:

                return None

        return None