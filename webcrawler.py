__author__ = 'xSp4rkz'

import mechanize # Used for setting up a browser to access websites on the internet
import cookielib # Used to store cookies and session information
import re # Used to execute regular expressions
from common import Echo # Used to echo information to the current output stream to display to user

class WWWConnection():

    def __init__(self):

        # Browser
        self.__Browser = mechanize.Browser() # Create an internet browser

        # Cookie Jar
        # Needed to handle sessions
        self.__CookieJar = cookielib.LWPCookieJar()
        self.__Browser.set_cookiejar(self.__CookieJar)

        # Browser Options
        self.__Browser.set_handle_equiv(True)
        self.__Browser.set_handle_redirect(True)
        self.__Browser.set_handle_referer(True)
        self.__Browser.set_handle_robots(False)
        self.__Browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1) # For redirects

        # Setup Headers to appear like a regular browser. Without this step the browser may be confused as a BOT and denied service from a website
        self.__Browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        # Object Variables
        self.__LoggedIn = False

    def __GetPageSource(self, WebsiteURL):

        # Connect to website
        Echo('Connecting to ' + WebsiteURL)
        self.__Browser.open(WebsiteURL)

        # Check response
        Response = self.__Browser.response()
        ResponseCode = Response.code

        # Make sure response is good
        if not ResponseCode == 200:  # Look for an 'OK' code (200)

            Echo('Uh Oh! Not sure what happened.. Hmmm...')
            Echo('\t- Received response: ' + ResponseCode + ' from server')
            Echo('\t - ERROR!!')

            raise Exception('Unable to connect to website. Unknown error. Maybe you did something wrong.')  # No point going any further

        # Store page source
        PageSource = Response.read()

        return PageSource

    def Login(self, Username, Password):
        pass