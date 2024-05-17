import os
import time
from unittest.mock import patch
from Libs.FolderBasedCache import FolderBasedCache

# make tmp dir
os.makedirs("./tests/tmp", exist_ok=True)


def teardown_module():
    cache = FolderBasedCache("./tests/tmp")


def test_persist():
    # create cache, set items, save, create new cache with new name on same folder and assert
    cache1 = FolderBasedCache("./tests/tmp")
    cache1.set("key1", "value1", 60)
    cache1.set("key2", "value2", 60)
    cache1.save()

    cache2 = FolderBasedCache("./tests/tmp")
    assert cache2.get("key1") == cache1.get("key1")
    assert cache2.get("key2") == cache1.get("key2")


def test_get_existing_key():
    # create cache, set item, get existing key
    cache = FolderBasedCache("./tests/tmp")
    cache.set("key", "value", 60)
    assert cache.get("key") == "value"


def test_get_nonexistent_key():
    # create cache, get nonexistent key
    cache = FolderBasedCache("./tests/tmp")
    assert cache.get("nonexistent_key") is None


def test_set_key():
    # create cache, set key, get key
    cache = FolderBasedCache("./tests/tmp")
    cache.set("key", "value", 60)
    assert cache.get("key") == "value"


def test_set_key_with_cache_duration():
    # create cache, set key with cache duration, get key before expiration, get key after expiration
    cache = FolderBasedCache("./tests/tmp")
    cache.set("key", "value", 2)  # cache duration of 2 seconds
    assert cache.get("key") == "value"  # key should be accessible immediately
    time.sleep(3)  # wait for cache to expire
    assert cache.get("key") is None  # key should be expired and inaccessible


def test_cleanup():
    # create cache, set key, cleanup cache, get key
    cache = FolderBasedCache("./tests/tmp")
    cache.set("key", "value", 1)
    time.sleep(2)
    cache.cleanup()
    assert cache.get("key") is None


def test_restore():
    # create cache, set key, save cache, cleanup cache, restore cache, get key
    cache = FolderBasedCache("./tests/tmp")
    cache.set("key", "value", 60)
    cache.save()
    cache.cleanup()
    cache.restore()
    assert cache.get("key") == "value"


def test_delete():
    cache = FolderBasedCache("./tests/tmp")
    cache.set("key", "value", 60)
    cache.save()
    cache.delete("key")
    assert cache.get("key") is None
