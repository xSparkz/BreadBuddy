import yaml # Used for writing and reading configuration files
import io # File functions

class Settings():

    def __init__(self, filename):

        self.filename = filename # Store the filename of the settings file
        self.settings = '' # Store the loaded settings

        with open(self.filename, 'r') as stream: # Open file

            self.settings = yaml.load(stream) # Load the settings

    def Set(self, key, data):

        self.settings[key] = data # Modify or Add the Setting

        with io.open(self.filename, 'w', encoding='utf8') as settingsfile: # Open the file

            yaml.dump(self.settings, settingsfile, default_flow_style=False, allow_unicode=True) # Write the data

    def Remove(self, key):

        del self.settings[key]

        with io.open(self.filename, 'w', encoding='utf8') as settingsfile: # Open the file

            yaml.dump(self.settings, settingsfile, default_flow_style=False, allow_unicode=True) # Write the data

    def Read(self, key):

        return self.settings[key] # Return a specific setting

    def ReadAll(self):

        return self.settings # Return all settings