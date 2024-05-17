import json
import os

# ConfigFile class
class ConfigFile:
    def __init__(self, filename):
        """
        Initializes a new instance of the ConfigFile class.

        Args:
            filename (str): The path to the configuration file.
        """
        self.filename = filename
        self.config = {}
        self.load()

    def load(self):
        """
        Loads the configuration from the specified file.

        Returns:
            bool: True if the configuration was successfully loaded, False otherwise.
        """
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.config = json.load(f)
            return True
        return False

    def save(self):
        """
        Saves the configuration to the file.
        """
        with open(self.filename, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key):
        """
        Retrieves the value associated with the specified key from the configuration.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Any: The value associated with the key, or None if the key does not exist.
        """
        return self.config.get(key, None)

    def set(self, key, value):
        """
        Sets the value for the specified key in the configuration.

        Args:
            key (str): The key to set the value for.
            value (Any): The value to set.

        """
        self.config[key] = value
        self.save()