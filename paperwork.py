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
import sqlite3 # Database support
import os # Directory and File operations
from common import CreateFolder
from PyQt4 import QtCore # GUI Support
from PyQt4 import QtGui # GUI Support

DATABASE_PAPERWORK = '/home/xsparkz/paperwork/paperwork.sqlite'

REGEX_DATE = 'DATE:\\s*(\\d+\\/\\d+\\/\\d+)'
REGEX_TIME = 'TIME:\\s*(\\d+:\\d+)'
REGEX_ROUTE_NUMBER = '(?:ROUTE#:|RTE#:)\\s*(\\d+)'
REGEX_INVOICE_NUMBER = 'INVOICE#:\\s*(\\d+)'
REGEX_CUSTOMER_NUMBER = '(?:CUSTOMER#:\\s*)(\\d+\\s*\\d+)'

REGEX_INLINE_VEHICLE = '(?:\\w|\\d)(VEHICLE#:)'
REGEX_INLINE_ROUTE = '(?:\\w|\\d)(ROUTE#:)'
REGEX_INLINE_REGION = '(?:\\w|\\d)(REGION#:)'
REGEX_INLINE_DATETIME = '(DATE:\\s+\\d+\\/\\d+\\/\\d+\\s+TIME:)'
REGEX_INLINE_PO_NUMBER = '(PO#:)'

class DataBase():

    def __init__(self):

        self.__Database = None  # Database Object
        self.__Cursor = None  # Cursor Object used to search databases

    def __del__(self):  # Cleanup

        if not self.__Database is None:

            self.__Database.commit()  # Commit the changes to the database
            self.__Database.close()  # Close the database

    def Connect(self):

        self.__Database = sqlite3.connect(DATABASE_PAPERWORK, check_same_thread=False)  # Connect to database
        self.__Cursor = self.__Database.cursor()  # Get a cursor so we can work with our database

        # Create table if it doesnt exist
        self.__Cursor.execute('''CREATE TABLE IF NOT EXISTS paperwork (
                id INTEGER PRIMARY KEY,
                date TEXT, 
                time TEXT,
                route_number TEXT,
                document_title TEXT,
                document BLOB UNIQUE)
                ;''')

        self.__Cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY,
                date TEXT, 
                time TEXT,
                route_number TEXT,
                invoice_number TEXT, 
                customer_number TEXT, 
                customer_name TEXT, 
                document BLOB UNIQUE)
                ;''')

        self.CommitChanges()

    def CommitChanges(self):

        self.__Database.commit()  # Commit changes to database

    def AddDocuments(self, Documents):

        for Document in Documents:

            if Document.isInvoice():

                self.__Cursor.execute('''INSERT or IGNORE INTO invoices(id, date, time, route_number, invoice_number, customer_number, customer_name, document) VALUES(NULL,?,?,?,?,?,?,?)''',
                                      (Document.Date(),
                                       Document.Time(),
                                       Document.RouteNumber(),
                                       Document.InvoiceNumber(),
                                       Document.CustomerNumber(),
                                       Document.CustomerName(),
                                       Document.DocumentToString()))
            else:
                self.__Cursor.execute('''INSERT or IGNORE INTO paperwork(id, date, time, route_number, document_title, document) VALUES(NULL,?,?,?,?,?)''',
                                      (Document.Date(),
                                       Document.Time(),
                                       Document.RouteNumber(),
                                       Document.Title(),
                                       Document.DocumentToString()))

        self.CommitChanges()

    def GetListOfRoutes(self):

        self.__Cursor.execute('''SELECT DISTINCT route_number FROM paperwork''') # Grab a list of unique route numbers
        return self.__Cursor.fetchall()

    def GetCustomerList(self, RouteNumber):

        self.__Cursor.execute('''SELECT DISTINCT customer_name FROM invoices WHERE route_number=?''', (RouteNumber,))  # Grab a list of unique route numbers
        return self.__Cursor.fetchall()

    def GetInvoices(self, RouteNumber):

        self.__Cursor.execute('''SELECT date, time, invoice_number, customer_name FROM invoices WHERE route_number=?''', (RouteNumber,))  # Grab a list of paperwork for a specific route
        return self.__Cursor.fetchall()

    def GetListOfPaperwork(self, RouteNumber):

        self.__Cursor.execute('''SELECT date, time, document_title FROM paperwork WHERE route_number=?''', (RouteNumber,))  # Grab a list of paperwork for a specific route
        return self.__Cursor.fetchall()

    def Close(self):
        self.__Database.close()


class Record():

    def __init__(self, Document):

        # Generic Document Traits
        self.__RouteNumber = None
        self.__Date = None
        self.__Time = None
        self.__DocumentTitle = ''
        self.__Document = Document # Store the document

        # Invoice Traits
        self.__isInvoice = False # Identifies the document as an invoice
        self.__InvoiceNumber = None
        self.__CustomerNumber = None
        self.__CustomerName = ''

        self.__IdentifyDocument() # Identify the document and populate the correct fields

    def RouteNumber(self):

        return self.__RouteNumber

    def Date(self, ):

        return self.__Date

    def Time(self):

        return self.__Time

    def isInvoice(self):

        return self.__isInvoice

    def InvoiceNumber(self):

        return self.__InvoiceNumber

    def CustomerNumber(self):

        return self.__CustomerNumber

    def CustomerName(self):

        return self.__CustomerName

    def Title(self):

        return self.__DocumentTitle

    def Document(self):

        return self.__Document

    def DocumentToString(self):

        DocumentString = '' # Create an empty string

        for Line in self.__Document:

            DocumentString = DocumentString + Line # Build the string

        return DocumentString

    def __IdentifyDocument(self):

        ReadingCustomerName = False # Used to extract the customer name
        LineNumber = 0 # Keep track of what line number we're currently at

        for Line in self.__Document:

            if ReadingCustomerName:

                Search = re.search(REGEX_INLINE_PO_NUMBER, Line)

                if Search != None:

                    ReadingCustomerName = False
                    self.__CustomerName = str(self.__CustomerName).strip() # Remove white spaces
                    continue  # Continue the loop from beginning

                else:

                    self.__CustomerName = self.__CustomerName + str(Line).strip() + ' '
                    continue # Continue the loop from beginning

            Search = re.search(REGEX_DATE, Line)

            if Search != None:
                self.__Date = Search.group(1)

            Search = re.search(REGEX_TIME, Line)

            if Search != None:
                self.__Time = Search.group(1)

            Search = re.search(REGEX_ROUTE_NUMBER, Line, re.IGNORECASE)

            if Search != None:
                self.__RouteNumber = Search.group(1)

            Search = re.search(REGEX_INVOICE_NUMBER, Line)

            if Search != None:
                self.__InvoiceNumber = Search.group(1)
                self.__isInvoice = True

            Search = re.search(REGEX_CUSTOMER_NUMBER, Line)

            if Search != None:
                self.__CustomerNumber = Search.group(1)
                ReadingCustomerName = True

        # Second Pass - to extract document title if its not an invoice
        if self.__isInvoice == False:

            LineNumber = 0  # Keep track of the line number we are currently at

            for Line in self.__Document:

                LineNumber += 1 # Increase the line number count

                if LineNumber > 2: # The first 2 lines are the header of the document so make sure we are looking past that for the document title

                    TempLine = str(Line).strip() # Remove white space from the current line

                    if len(TempLine) > 2: # If we still have characters in the line after stripping the whitespace then we are probably looking at the document title

                        self.__DocumentTitle = TempLine # Save the document title
                        break # Stop the loop since we found the title


class PaperWork():

    def __init__(self, MainWindow):

        self.__SplitLines = None # Store the lines that were split
        self.__NumberOfFixes = 0 # Keep track of the amount of lines that were fixed

        self.__MainWindow = MainWindow  # Set a reference to the Main Window so we can manipulate it from here

        # Controls -------------------------
        self.__MainWindow.datePaperworkFrom.setDate(QtCore.QDate.currentDate())
        self.__MainWindow.datePaperworkTo.setDate(QtCore.QDate.currentDate())
        self.__MainWindow.datePaperworkTo.setMinimumDate(QtCore.QDate.currentDate())  # Date cannot be sooner than the from date

        # Table - Paperwork -----------------
        TableHeader = self.__MainWindow.tableInvoices.horizontalHeader()
        TableHeader.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        TableHeader.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        TableHeader.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        TableHeader.setResizeMode(3, QtGui.QHeaderView.Stretch)

        # Table - Invoices -----------------
        TableHeader = self.__MainWindow.tablePaperwork.horizontalHeader()
        TableHeader.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        TableHeader.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        TableHeader.setResizeMode(2, QtGui.QHeaderView.Stretch)

        # Events Handlers ------------------
        self.__MainWindow.btnPaperworkRefresh.clicked.connect(self.__Button_Refresh_Clicked)
        self.__MainWindow.btnPaperworkDownload.clicked.connect(self.__Button_Download_Clicked)
        self.__MainWindow.comboRouteNumber.currentIndexChanged.connect(self.__Combo_Route_Changed)
        self.__MainWindow.datePaperworkFrom.dateChanged.connect(self.__Date_Paperwork_From_Changed)

        # Database Handlers ----------------
        self.__Database = DataBase()
        self.__Database.Connect()

    @staticmethod
    def __FixLine(LineToFix, SplitToken):

        TempLines = str(LineToFix).split(SplitToken)  # Split the lines in two using the split token
        TempLines[0] = TempLines[0] + '\n\n\n'  # Add new lines after the line we just split
        TempLines[1] = SplitToken + TempLines[1]  # Piece the line back together with the split token that was removed

        return TempLines # Return a 2 element array with the two fixed lines

    @staticmethod
    def __RemoveBlankLinesAtEndOfList(Source):

        FixedList = Source # Make a copy of the list

        while len(FixedList[-1]) <= 2: # Continue loop while the last line continues to be blank

            FixedList.pop() # Remove the blank line

        return FixedList # Return the new fixed list

    def __Fix(self, Filename):

        Document = [] # Create a new document list to store the fixed file

        with open(Filename, 'r') as LinesFromFile:

            for Line in LinesFromFile: # Run through every line in the file

                self.__SplitLines = None # Reset this variable to none so we know how to write lines to the temp file later

                # EXAMPLE LINE: SignatureREGION#:             ROUTE#:206555 DRIVER#:206555   DATE:   7/21/17 TIME:01:34
                if re.search(REGEX_INLINE_ROUTE, Line) != None: # Found a broken line

                    self.__SplitLines = self.__FixLine(Line, 'ROUTE#:') # Split the lines in two using ROUTE#: as the split token
                    self.__NumberOfFixes += 1 # Increase the number of fixes made

                if re.search(REGEX_INLINE_VEHICLE, Line) != None:  # Found a broken line

                    self.__SplitLines = self.__FixLine(Line, 'VEHICLE#:')  # Split the lines in two using VEHICLE#: as the split token
                    self.__NumberOfFixes += 1  # Increase the number of fixes made

                if re.search(REGEX_INLINE_REGION, Line) != None:  # Found a broken line

                    self.__SplitLines = self.__FixLine(Line, 'REGION#:')  # Split the lines in two using REGION#: as the split token
                    self.__NumberOfFixes += 1  # Increase the number of fixes made

                if self.__SplitLines != None: # Did we end up fixing a line?

                    Document.append(self.__SplitLines[0])  # Write line 1
                    Document.append(self.__SplitLines[1])  # Write line 2

                    continue # Start at beginning

                Document.append(Line) # Write the line as is without any changes

        return Document # Return the fixed document

    def Parse(self, Filename):

        LinesFromFile = self.__Fix(Filename) # Store the file as a list after it's been fixed

        Document = [] # Create a new list to store the parsed document before saving
        Documents = [] # Create a list to store all of the parsed documents

        for Line in LinesFromFile:  # Run through every line in the file

            if re.search(REGEX_INLINE_DATETIME, Line) != None:  # Found a new document header

                if len(Document) > 0: # If the document isn't empty then save the existing document to start another

                    Documents.append(Record(self.__RemoveBlankLinesAtEndOfList(Document))) # Add the document to the list of documents after removing the blank lines at the end of the document
                    Document = [] # Clear the current document

            Document.append(Line) # Add the current line to the current document

        if len(Document) > 0: # Check to make sure the document is empty, if its not then add it to the documents list

            Documents.append(Record(self.__RemoveBlankLinesAtEndOfList(Document)))  # Add the document to the list of documents after removing the blank lines at the end of the document

        # Save the documents to individual files
        FileNum = 0
        TempFolder = '/home/xsparkz/paperwork/handheld/'
        CreateFolder(TempFolder) # Make sure it exists. Create it if not

        self.__Database.AddDocuments(Documents)

    def SortFilesFromDirectory(self, DirectoryToSort):

        for file in os.listdir("/mydir"):
            if file.endswith(".txt"):
                print(os.path.join("/mydir", file))

    def __Button_Refresh_Clicked(self):

        self.__MainWindow.comboRouteNumber.clear()

        for Route in self.__Database.GetListOfRoutes():

            self.__MainWindow.comboRouteNumber.addItem(QtCore.QString(Route[0])) # Add route number to list of routes

    def __Button_Download_Clicked(self):
         
        self.Parse('/home/xsparkz/PycharmProjects/BreadBuddy/txt/paperwork.txt')

    def __Date_Paperwork_From_Changed(self, Date):

        self.__MainWindow.datePaperworkTo.setMinimumDate(Date)  # Date cannot be sooner than the from date
        self.__MainWindow.datePaperworkTo.setDate(Date) # Set the (to) date to the same date as the from date

    def __Combo_Route_Changed(self):

        RouteNumber = str(self.__MainWindow.comboRouteNumber.itemText(self.__MainWindow.comboRouteNumber.currentIndex()))
        Customers = self.__Database.GetCustomerList(RouteNumber)

        self.__MainWindow.comboCustomers.clear()
        self.__MainWindow.comboCustomers.addItem(QtCore.QString('All Customers'))

        for Customer in Customers:

            self.__MainWindow.comboCustomers.addItem(QtCore.QString(Customer[0]))

        PaperWork = self.__Database.GetListOfPaperwork(RouteNumber)
        self.__MainWindow.tablePaperwork.clear() # Clear the contents of the table
        self.__MainWindow.tablePaperwork.setRowCount(0) # Remove the left over rows

        for Document in PaperWork:

            rowPosition = self.__MainWindow.tablePaperwork.rowCount() # Grab last row
            self.__MainWindow.tablePaperwork.insertRow(rowPosition) # Insert a new empty row after the last
            self.__MainWindow.tablePaperwork.setItem(rowPosition, 0, QtGui.QTableWidgetItem(Document[0])) # Date
            self.__MainWindow.tablePaperwork.setItem(rowPosition, 1, QtGui.QTableWidgetItem(Document[1])) # Time
            self.__MainWindow.tablePaperwork.setItem(rowPosition, 2, QtGui.QTableWidgetItem(Document[2])) # Customer Name

        self.__MainWindow.tablePaperwork.removeRow(0) # Remove the first empty row

        Headers = QtCore.QStringList() # Create a new header
        Headers.append(QtCore.QString('Date'))
        Headers.append(QtCore.QString('Time'))
        Headers.append(QtCore.QString('Document Title'))

        self.__MainWindow.tablePaperwork.setHorizontalHeaderLabels(Headers)

        Invoices = self.__Database.GetInvoices(RouteNumber)
        self.__MainWindow.tableInvoices.clear()  # Clear the contents of the table
        self.__MainWindow.tableInvoices.setRowCount(0)  # Remove the left over rows

        for Document in Invoices:
            rowPosition = self.__MainWindow.tableInvoices.rowCount()  # Grab last row
            self.__MainWindow.tableInvoices.insertRow(rowPosition)  # Insert a new empty row after the last
            self.__MainWindow.tableInvoices.setItem(rowPosition, 0, QtGui.QTableWidgetItem(Document[0]))  # Date
            self.__MainWindow.tableInvoices.setItem(rowPosition, 1, QtGui.QTableWidgetItem(Document[1]))  # Time
            self.__MainWindow.tableInvoices.setItem(rowPosition, 2, QtGui.QTableWidgetItem(Document[2]))  # Customer Name
            self.__MainWindow.tableInvoices.setItem(rowPosition, 3, QtGui.QTableWidgetItem(Document[3]))  # Invoice #

        self.__MainWindow.tableInvoices.removeRow(0)  # Remove the first empty row

        Headers = QtCore.QStringList()  # Create a new header
        Headers.append(QtCore.QString('Date'))
        Headers.append(QtCore.QString('Time'))
        Headers.append(QtCore.QString('Invoice #'))
        Headers.append(QtCore.QString('Customer'))

        self.__MainWindow.tableInvoices.setHorizontalHeaderLabels(Headers)


