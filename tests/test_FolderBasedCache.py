import unittest
from setup import setupUnitTest
setupUnitTest()

from unittest.mock import patch
from Libs.FolderBasedCache import FolderBasedCache
import os
import jsonpickle
import time

class TestFolderBasedCache(unittest.TestCase):
    def setUp(self):
        os.makedirs("./tests/tmp", exist_ok=True)
        self.cache = FolderBasedCache("./tests/tmp")

    def tearDown(self):
        # Clean up any files created during the tests
        for file in os.listdir(self.cache.folder):
            os.remove(f"{self.cache.folder}/{file}")
        os.rmdir(self.cache.folder)



    def test_persist(self):
        # create cache, set items, save, create new cache with new name on same folder and assert
        cache1 = FolderBasedCache("./tests/tmp")
        cache1.set("key1", "value1", 60)
        cache1.set("key2", "value2", 60)
        cache1.save()

        cache2 = FolderBasedCache("./tests/tmp")
        self.assertEqual(cache2.get("key1"), cache1.get("key1"))
        self.assertEqual(cache2.get("key2"), cache1.get("key2"))
        
if __name__ == "__main__":
    unittest.main()