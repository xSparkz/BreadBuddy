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

import yaml # Used for writing and reading configuration files
import io # File functions

class Settings():

    def __init__(self, filename):

        self.filename = filename # Store the filename of the settings file
        self.settings = '' # Store the loaded settings

        with open(self.filename, 'r') as stream: # Open file

            self.settings = yaml.load(stream) # Load the settings

    def Set(self, key, data):

        try:
            self.settings[key] = data # Modify or Add the Setting

            with io.open(self.filename, 'w', encoding='utf8') as settingsfile: # Open the file

                yaml.dump(self.settings, settingsfile, default_flow_style=False, allow_unicode=True) # Write the data

        except:
            pass # Ignore errors

    def Remove(self, key):

        try:

            del self.settings[key]

            with io.open(self.filename, 'w', encoding='utf8') as settingsfile: # Open the file

                yaml.dump(self.settings, settingsfile, default_flow_style=False, allow_unicode=True) # Write the data

        except:
            pass # Ignore errors

    def Read(self, key):

        try:
            return self.settings[key] # Return a specific setting

        except:
            pass # Ignore errors (occurs if a usename is removed and attempted to be read)

    def ReadAll(self):

        try:
            return self.settings # Return all settings

        except:
            pass # Ignore errors (occurs if a usename is removed and attempted to be read)