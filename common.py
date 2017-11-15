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

import re # Regular Expression Support
import os # Operating System File Support
from PyQt4.QtGui import QMessageBox

# URL's
URL_LOGIN = 'https://orders.westonfoods.ca/edistributor/'

# Regular Expressions
REGEX_ORDER_STORENAME = '<span id="ctl00_main_ucCustomerOrder_lblCustInfoLeft" style="font-size:14px;font-weight:bold;">([\\s\\S]*?)<\\/span>' # ACCOUNT NAME<br/>10000000 - STORE NAME
REGEX_ORDER_STOREADDRESS = '<span id="ctl00_main_ucCustomerOrder_lblCustInfoRight" style="font-size:14px;font-weight:bold;">([\\s\\S]*?)<\\/span>' # 199 SOME ST<br/>CITY, ON, L1L 2A2
REGEX_ROUTE_NAME_AND_NUMBER = '<br>Route: ([\\s\\S]*?)<\\/span>' # <br>Route: 555555, OWNER NAME</span>

def Echo(lineToEcho):

    print lineToEcho

def RegExFind(String, Pattern):

    SearchResult = re.search(Pattern, String) # Regular Expression search

    if SearchResult:
        return SearchResult.group(1) # Return the found substring

    else:
        return None # No results found

def CreateFolder(Foldername):

    if not os.path.exists(Foldername): # Check to make sure it doesn't already exist

        os.makedirs(Foldername) # Create the folder