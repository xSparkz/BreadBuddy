__author__ = 'xSp4rkz'

import sys # Used to supply argv to application
import gui # All of the GUI code independent from functional code
from PyQt4 import QtGui # Library for working with GUI
from PyQt4.QtCore import QObject # Used to work with Gui Objects
import os # Used to manipulate files and folders
from settings import Settings

class BreadBuddyGui(QtGui.QMainWindow, gui.Ui_MainWindow):

    def __init__(self, parent=None):

        super(BreadBuddyGui, self).__init__(parent)
        self.setupUi(self)

class Application(QObject):

    def __init__(self):

        QObject.__init__(self)  # initialisation required for object inheritance

        self.MainApp = QtGui.QApplication(sys.argv) # Setup main application
        self.MainWindow = BreadBuddyGui() # Setup main window

        self.Passwords = Settings('config/passwords.yml') # Load the passwords file
        self.Settings = Settings('config/settings.yml') # Load the settings file

        # Load Passwords -----------------
        self.LoadPasswords() # Load all the Usernames into the drop down box

        # Events Handlers ------------------
        self.MainWindow.btnLogin.clicked.connect(self.Button_Login_Clicked)
        self.MainWindow.btnForget.clicked.connect(self.Button_Forget_Clicked)
        self.MainWindow.comboAccounts.currentIndexChanged.connect(self.Combo_SelectItem_Accounts)

    def LoadPasswords(self):

        self.MainWindow.comboAccounts.clear() # Clear all stored user names from the drop down box

        UserNames = self.Passwords.ReadAll() # Grab all the stored user names

        for UserName in UserNames: # Run through all the user names

            self.MainWindow.comboAccounts.addItem(UserName) # Add username to drop down box

        self.MainWindow.txtUsername.setText(self.MainWindow.comboAccounts.currentText())
        self.MainWindow.txtPassword.setText(UserNames[str(self.MainWindow.comboAccounts.currentText())])

    def Combo_SelectItem_Accounts(self):

        Username = str(self.MainWindow.comboAccounts.currentText())

        self.MainWindow.txtUsername.setText(Username)
        self.MainWindow.txtPassword.setText(self.Passwords.Read(Username))

    def Button_Forget_Clicked(self):

        self.Passwords.Remove(str(self.MainWindow.comboAccounts.currentText()))
        self.LoadPasswords()

    def Button_Login_Clicked(self):

        UserName = str(self.MainWindow.txtUsername.text()) # Store username from textbox
        Password = str(self.MainWindow.txtPassword.text()) # Store password from textbox

        if self.MainWindow.checkboxRememberAccount.isChecked(): # Are we saving passwords?

            self.Passwords.Set(UserName, Password) # Save the password to file

    def Run(self):

        self.MainWindow.show() # Show the Main Window
        self.MainApp.exec_() # Run the GUI Framework


if __name__ == '__main__':

    BreadBuddy = Application() # Initialize the application
    BreadBuddy.Run() # Run the application