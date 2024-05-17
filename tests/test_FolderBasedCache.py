import unittest
from unittest.mock import patch
from FolderBasedCache import FolderBasedCache

class TestFolderBasedCache(unittest.TestCase):
    def setUp(self):
        self.cache = FolderBasedCache("/path/to/cache")

    def tearDown(self):
        # Clean up any files created during the tests
        for file in os.listdir(self.cache.folder):
            os.remove(f"{self.cache.folder}/{file}")

    def test_load_existing_cache(self):
        # Create a mock durations.json file
        durations = {
            "file1": 1234567890,
            "file2": 9876543210
        }
        with open(f"{self.cache.folder}/durations.json", "w") as f:
            f.write(jsonpickle.encode(durations))

        # Create mock cache files
        cache_data = {
            "file1": {"key1": "value1"},
            "file2": {"key2": "value2"}
        }
        for file, data in cache_data.items():
            with open(f"{self.cache.folder}/{file}", "w") as f:
                f.write(jsonpickle.encode(data))

        # Call the load method
        self.cache.load()

        # Assert that the cache and cache_durations are loaded correctly
        self.assertEqual(self.cache.cache, cache_data)
        self.assertEqual(self.cache.cache_durations, durations)

    def test_load_empty_cache(self):
        # Call the load method on an empty cache folder
        self.cache.load()

        # Assert that the cache and cache_durations are empty
        self.assertEqual(self.cache.cache, {})
        self.assertEqual(self.cache.cache_durations, {})

    def test_load_no_durations_file(self):
        # Create mock cache files
        cache_data = {
            "file1": {"key1": "value1"},
            "file2": {"key2": "value2"}
        }
        for file, data in cache_data.items():
            with open(f"{self.cache.folder}/{file}", "w") as f:
                f.write(jsonpickle.encode(data))

        # Call the load method
        self.cache.load()

        # Assert that the cache and cache_durations are loaded correctly
        self.assertEqual(self.cache.cache, cache_data)
        self.assertEqual(self.cache.cache_durations, {})

    def test_persist(self):
        # Create a mock cache
        cache_data = {
            "file1": {"key1": "value1"},
            "file2": {"key2": "value2"}
        }
        self.cache.cache = cache_data

        # Call the persist method
        self.cache.persist()

        # Assert that the cache files are created correctly
        for file, data in cache_data.items():
            with open(f"{self.cache.folder}/{file}", "r") as f:
                self.assertEqual(jsonpickle.decode(f.read()), data)

        # Assert that the cache_durations file is created correctly
        with open(f"{self.cache.folder}/durations.json", "r") as f:
            self.assertEqual(jsonpickle.decode(f.read()), {})
if __name__ == "__main__":
    unittest.main()