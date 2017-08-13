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

import sys # Used to supply argv to application
import gui # All of the GUI code independent from functional code
from PyQt4 import QtGui # Library for working with GUI
from PyQt4.QtCore import QObject # Used to work with Gui Objects
import os # Used to manipulate files and folders
from settings import Settings
import passwords

class BreadBuddyGui(QtGui.QMainWindow, gui.Ui_MainWindow):

    def __init__(self, parent=None):

        super(BreadBuddyGui, self).__init__(parent)
        self.setupUi(self)

class Application(QObject):

    def __init__(self):

        QObject.__init__(self)  # initialisation required for object inheritance

        self.MainApp = QtGui.QApplication(sys.argv) # Setup main application
        self.MainWindow = BreadBuddyGui() # Setup main window

        self.Settings = Settings('config/settings.yml') # Load the settings file

        # Load Passwords -----------------
        self.Passwords = passwords.Passwords(self.MainWindow)
        self.Passwords.LoadPasswords() # Load all the Usernames into the drop down box

        # Events Handlers ------------------
        self.MainWindow.btnLogin.clicked.connect(self.Passwords.Button_Login_Clicked)
        self.MainWindow.btnForget.clicked.connect(self.Passwords.Button_Forget_Clicked)
        self.MainWindow.comboAccounts.currentIndexChanged.connect(self.Passwords.Combo_SelectItem_Accounts)

    def Run(self):

        self.MainWindow.show() # Show the Main Window
        self.MainApp.exec_() # Run the GUI Framework

if __name__ == '__main__':

    BreadBuddy = Application() # Initialize the application
    BreadBuddy.Run() # Run the application