import unittest
from setup import setupUnitTest
setupUnitTest()

from Libs.ConfigFile import ConfigFile
import os
import jsonpickle


class TestConfigFile(unittest.TestCase):


    def setUp(self):
        os.makedirs("./tests/tmp", exist_ok=True)
    def tearDown(self):
        # Clean up any files created during the tests
        for file in os.listdir("./tests/tmp"):
            os.remove(f"./tests/tmp/{file}")
        os.rmdir("./tests/tmp")

    def test_init(self):
        # Test with an existing file
        filename = "./tests/tmp/file.json"
        config_file = ConfigFile(filename)
        self.assertEqual(config_file.filename, filename)
        self.assertEqual(config_file.config, {})
        
        # Test with a non-existing file
        filename = "./tests/tmp/non_existent_file.json"
        config_file = ConfigFile(filename)
        self.assertEqual(config_file.filename, filename)
        self.assertEqual(config_file.config, {})

    def test_load(self):
        # Create a mock config file
        filename = "./tests/tmp/config.json"
        config_data = {
            "key1": "value1",
            "key2": "value2"
        }
        with open(filename, "w") as f:
            f.write(jsonpickle.encode(config_data))

    def test_persist(self):
        # Create a mock config file
        filename = "./tests/tmp/config.json"
        # Create a ConfigFile object
        config_file1 = ConfigFile(filename)
        config_file1.save()      
         
        # Create a ConfigFile object 2
        config_file2 = ConfigFile(filename)
        assert config_file2.config == config_file1.config

if __name__ == "__main__":
    unittest.main()