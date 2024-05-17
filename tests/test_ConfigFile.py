import unittest
import sys
import os

if not os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) in sys.path:
    # Add the project root directory to the sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from Libs.ConfigFile import ConfigFile
import os
import jsonpickle
import pytest
import os
import jsonpickle
from Libs.ConfigFile import ConfigFile


def setup_module():
    os.makedirs("./tests/tmp", exist_ok=True)


@pytest.fixture
def config_file():
    filename = "./tests/tmp/config.json"
    config_file = ConfigFile(filename)
    yield config_file
    os.remove(filename)


def teardown_module():
    os.rmdir("./tests/tmp")


def test_init_existing_file(config_file):
    assert config_file.filename == "./tests/tmp/config.json"
    assert config_file.config == {}


def test_init_non_existing_file(config_file):
    filename = "./tests/tmp/non_existent_file.json"
    config_file = ConfigFile(filename)
    assert config_file.filename == filename
    assert config_file.config == {}


def test_load(config_file):
    config_data = {"key1": "value1", "key2": "value2"}
    with open(config_file.filename, "w") as f:
        f.write(jsonpickle.encode(config_data))

    config_file.load()
    assert config_file.config == config_data


def test_set(config_file):
    config_file.set("key1", "value1")
    assert config_file.config["key1"] == "value1"


def test_save(config_file):
    config_file.set("key1", "value1")
    config_file.set("key2", "value2")
    config_file.save()

    with open(config_file.filename, "r") as f:
        saved_data = jsonpickle.decode(f.read())

    assert saved_data == config_file.config


if __name__ == "__main__":
    pytest.main()
