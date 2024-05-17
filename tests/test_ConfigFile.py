import unittest
from ConfigFile import ConfigFile


class TestConfigFile(unittest.TestCase):
    def test_init(self):
        # Test with an existing file
        filename = "/path/to/existing/file.json"
        config_file = ConfigFile(filename)
        self.assertEqual(config_file.filename, filename)
        self.assertEqual(config_file.config, {})
        
        # Test with a non-existing file
        filename = "/path/to/non_existing/file.json"
        config_file = ConfigFile(filename)
        self.assertEqual(config_file.filename, filename)
        self.assertEqual(config_file.config, {})
        
    def test_load(self):
        # Create a mock config file
        filename = "/path/to/config.json"
        config_data = {
            "key1": "value1",
            "key2": "value2"
        }
        with open(filename, "w") as f:
            f.write(jsonpickle.encode(config_data))

    def test_persist(self):
        # Create a mock config file
        filename = "/path/to/config.json"
        # Create a ConfigFile object
        config_file1 = ConfigFile(filename)
        config_file1.save()      
         
        # Create a ConfigFile object 2
        config_file2 = ConfigFile(filename)
        assert config_file2.config == config_file1.config

if __name__ == "__main__":
    unittest.main()