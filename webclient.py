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

import mechanize # Web browser support
import cookielib # Cookie handling
import re # Regular Expression Support
import os # Operating system functions
import ssl
from bs4 import BeautifulSoup
from common import Echo
from settings import *

LINK_BASE_URL = 'https://orders.westonfoods.ca/'
LINK_BASE_ORDERS = LINK_BASE_URL + 'eDistributor/Secure/Distributor/'
LINK_ORDERS = 'https://orders.westonfoods.ca/eDistributor/Login.aspx'
LINK_INTRANET = 'https://distributors.westonfoods.ca/_layouts/customlogin.aspx?ReturnUrl=%2f'
LINK_INTRANET_REPORTS = 'https://distributors.westonfoods.ca/Report/default.aspx'

class WebConnection():

    def __init__(self):

        #Authentication
        self._LoggedIn = False

        self._Username = None
        self._Password = None

        #Browser
        self._Browser = mechanize.Browser() # Create a new web browser object

        #Cookie Jar
        self._CookieJar = cookielib.LWPCookieJar() # Create a cookie jar to handle site cookies
        self._Browser.set_cookiejar(self._CookieJar)  # Connect the cookie jar to the browser object

        #Browser Options
        self._Browser.set_handle_equiv(True)
        self._Browser.set_handle_redirect(True) # Automatically follow redirects
        self._Browser.set_handle_referer(True)
        self._Browser.set_handle_robots(False)

        self._Browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    def SetPassword(self, Password):

        self._Password = Password # Set the password

    def SetUserName(self, UserName):

        self._Username = UserName # Set the username

    def _CheckCredentials(self):

        if self._Username == None or self._Password == None:

            raise ValueError('ERROR: Username or Password not set.') # Raise an error if the username or password aren't set to avoid unexpected behavior

    def _EnsureLoggedIn(self):

        if self._LoggedIn == False:

            raise ValueError('ERROR: Not logged in.')

    def _GetPage(self, URL):

        print 'GET ' + URL

        # Connect
        self._Browser.open(URL)

        Response = self._Browser.response()

        if not Response.code == 200:  # If the response isn't ok then assume something wen't wrong

            raise ValueError('ERROR: Unable to retrieve webpage Received Reponse: ' + Response.code)

        return self._Browser.response()

    def _DownloadFile(self, URL, DirToSaveFileTo, FileName=None):

        FileToSave = FileName

        if FileToSave == None:

            TempFileName = str(URL).rsplit('/', 1)
            FileToSave = TempFileName[1] # Extract the filename from the URL

        print 'DOWNLOAD ' + FileToSave

        return self._Browser.retrieve(URL, os.path.join(DirToSaveFileTo, FileToSave))[0]

    def _GetLinks(self):

        return self._Browser.links() # link.text, link.url


class IntranetPortal(WebConnection):

    def __init__(self):

        WebConnection.__init__(self)

        self.__BASELINK = 'https://distributors.westonfoods.ca'

        # -------------- REGULAR EXPRESSIONS -----------------------------------------------------------
        self.__REGEX_INTRANET_LOGIN_FAILED = '(ctl00_PlaceHolderMain_login_FailureText)'
        self.__REGEX_INTRANET_INLINE_LINK_REPORT = '(\\/Report\\/\\d+[\\d|\\w]+\\/Forms\\/AllItems.aspx)'
        self.__REGEX_INRANET_INLINE_HANDHELD_REPORT = '(\\/Report\\/\\d+\\w+\\/HandheldPaperwork)'
        self.__REGEX_INRANET_INLINE_RSS_FEED_LINK = '(?:<link rel="alternate" type="application\\/rss\\+xml" title=".*href=")(.+)(?:">)'
        self.__REGEX_INRANET_RSS_FEED_LINK = '(?:<link>)(.+ID=\\d+)(?:<\\/link>)'
        self.__REGEX_INRANET_RSS_ITEM = '(?:<a href=")(.+)(?:" onclick="DispDocItemEx)'

    def Login(self):

        # Check to make sure login credentials are available (safety check)
        self._CheckCredentials()

        # Reset login status
        self._LoggedIn = False

        Response = self._GetPage(LINK_INTRANET) # Get login page

        # Login Form -------------------------------

        self._Browser.select_form("aspnetForm") # Select the correct form to fill out
        self._Browser['ctl00$PlaceHolderMain$login$UserName'] = self._Username # Fill in the username
        self._Browser['ctl00$PlaceHolderMain$login$password'] = self._Password # Fill in the password
        self._Browser.method = "POST" # Change the method of submission to POST instead of GET

        Response = self._Browser.submit() # Submit the form and complete the login process

        if Response.code == 200:

            SourceCode = Response.read()

            Search = re.search(self.__REGEX_INTRANET_LOGIN_FAILED, SourceCode) # Check the page to see if the login was unsuccessful

            if Search != None: # Found the text indicating that the login was unsuccessful

                return False # Failed Login (Incorrect Username or Password)

            else:

                self._LoggedIn = True # We have succesfully logged in
                return True

        return False # If we made it this far then the login was not successful. Something unexpected happened. Probably an error retrieving the login page

    @staticmethod
    def __GenerateLink(BaseURL, Link):

        Search = re.search('(https:\\/\\/[a-z|.]+)', BaseURL)  # Extract the base URL to reconstruct the link

        if Search != None:  # Looks like we found something

            return Search.group(1) + Link  # Re-construct the link

        else:

            return None

    def GetReports(self, DirToSaveReports):

        self._EnsureLoggedIn() # Make sure we are logged in

        Response = self._GetPage(LINK_INTRANET_REPORTS) # Get the reports page

        LinksToReports = [] # Create an empty list to store the links to each report page

        # ------------------------ FIND LINKS TO REPORTS _------------------------------
        for Link in self._GetLinks(): # Scan through all the links on the page

            CurrentLink = self.__GenerateLink(Link.base_url, Link.url) # Each link has to be re-constructed using the base URL

            Search = re.search(self.__REGEX_INTRANET_INLINE_LINK_REPORT, CurrentLink)  # Check each link to see if its a link to reports

            if Search != None:  # Looks like we found something

                LinksToReports.append(CurrentLink) # Add the URL to the list of links

        # -------- VISIT EACH REPORT LINK FOUND AND FIND THE LINK TO THE RSS FEED_-------
        RSSFeeds = [] # Create list to keep track of each RSS feed that contains reports for each route found

        for Link in LinksToReports:

            Response = self._GetPage(Link)  # Get the page

            Search = re.search(self.__REGEX_INRANET_INLINE_RSS_FEED_LINK, Response.read())  # Check the source code for the RSS feed link

            if Search != None:  # Looks like we found something

                RSSFeeds.append(self.__BASELINK + Search.group(1)) # Glue the link together and add to the list of RSS Feeds found

        # ------ VISIT ALL THE RSS FEEDS FOUND AND SCAN THROUGH EACH ITEM. VISIT EACH ITEM AND DOWNLOAD IT ------
        RSSItems = [] # Create a new list to keep track of each RSS Item that needs to be downloaded
        print 'RSS Items:'
        for RSSLink in RSSFeeds:

            Response = self._GetPage(RSSLink)  # Get the page

            for Item in re.finditer(self.__REGEX_INRANET_RSS_FEED_LINK, Response.read()): # Find all the item links on the RSS Feed Page

                RSSItems.append(Item.group(1)) # Add the item to the list of RSS Items

        FilesToDownload = [] # Create a new list of files to download

        for Item in RSSItems:

            Response = self._GetPage(Item) # Get the page

            Search = re.search(self.__REGEX_INRANET_RSS_ITEM, Response.read())  # Check the source code for the RSS feed item link

            if Search != None:  # Looks like we found something

                FilesToDownload.append(self.__BASELINK + Search.group(1))  # Glue the link together and add to the list of files to download


        # --------------------- DOWNLOAD EACH FILE ---------------------------
        #todo add progress
        for File in FilesToDownload:

            self._DownloadFile(File, DirToSaveReports)









class OrdersPortal(WebConnection):

    def __init__(self):
        pass

    def Login(self):

        #Safety check
        if not self._CheckCredentials(): return

        #Connect
        self._Browser.open(LINK_LOGIN)

        Response = self._Browser.response()
        ResponseCode = Response.code
        SourceCode = Response.read()

        if not ResponseCode == 200:

            Echo('Uh Oh! Something happened. Not sure what.')
            Echo(('\t- Received response: ' + ResponseCode + ' from server'))
            Echo('\t - Login failed!')

            return False

        #Login

        self._Browser.select_form("aspnetForm")
        self._Browser['ctl00$main$txtUserName'] = self._Username
        self._Browser['ctl00$main$txtPassword'] = self._Password
        self._Browser.method = "POST"

        Response = self._Browser.submit()
        ResponseCode = Response.code
        SourceCode = Response.read()