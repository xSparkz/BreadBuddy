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

from settings import Settings

class Passwords():

    def __init__(self, MainWindow):

        self.__MainWindow = MainWindow # Set a reference to the Main Window so we can manipulate it from here
        self.__Passwords = Settings('config/passwords.yml')  # Load the passwords file

        # Events Handlers ------------------
        self.__MainWindow.btnLogin.clicked.connect(self.__Button_Login_Clicked)
        self.__MainWindow.btnForget.clicked.connect(self.__Button_Forget_Clicked)
        self.__MainWindow.comboAccounts.currentIndexChanged.connect(self.__Combo_SelectItem_Accounts)

    def LoadPasswords(self):
        self.__MainWindow.comboAccounts.clear()  # Clear all stored user names from the drop down box

        UserNames = self.__Passwords.ReadAll()  # Grab all the stored user names

        for UserName in UserNames:  # Run through all the user names

            self.__MainWindow.comboAccounts.addItem(UserName)  # Add username to drop down box

        self.__MainWindow.txtUsername.setText(self.__MainWindow.comboAccounts.currentText())
        self.__MainWindow.txtPassword.setText(UserNames[str(self.__MainWindow.comboAccounts.currentText())])


    def __Combo_SelectItem_Accounts(self):

        try:
            Username = str(self.__MainWindow.comboAccounts.currentText())

            self.__MainWindow.txtUsername.setText(Username)
            self.__MainWindow.txtPassword.setText(self.__Passwords.Read(Username))

        except:
            pass


    def __Button_Forget_Clicked(self):
        self.__Passwords.Remove(str(self.__MainWindow.comboAccounts.currentText()))
        self.LoadPasswords()


    def __Button_Login_Clicked(self):
        UserName = str(self.__MainWindow.txtUsername.text())  # Store username from textbox
        Password = str(self.__MainWindow.txtPassword.text())  # Store password from textbox

        if self.__MainWindow.checkboxRememberAccount.isChecked():  # Are we saving passwords?

            self.__Passwords.Set(UserName, Password)  # Save the password to file
            self.__MainWindow.comboAccounts.addItem(UserName)  # Add username to drop down box
