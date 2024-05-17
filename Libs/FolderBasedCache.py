import jsonpickle
import os
import time
class FolderBasedCache():
    def __init__(self, folder):
        self.folder = folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.cache = {}
        self.cache_durations = {}
        self.load()
    
    def load(self):
        if os.path.exists(f"{self.folder}/durations.json"):
            with open(f"{self.folder}/durations.json", "r") as f:
                self.cache_durations = jsonpickle.decode(f.read())
            for file in os.listdir(self.folder):
                with open(f"{self.folder}/{file}", "r") as f:
                    self.cache[file] = jsonpickle.decode(f.read())
        else:
            for file in os.listdir(self.folder):
                os.remove(f"{self.folder}/{file}")
            
    def save(self):
        for key in self.cache:
            with open(f"{self.folder}/{key}", "w") as f:
                f.write(jsonpickle.encode(self.cache[key]))
        with open(f"{self.folder}/durations.json", "w") as f:
            f.write(jsonpickle.encode(self.cache_durations))

    def get(self, key):
        self.cleanup()
        return self.cache.get(key, None)
    def set(self, key, value, cache_duration):
        self.cache[key] = value
        self.cache_durations[key] = time.time() + cache_duration
        self.save()
    def cleanup(self):
        for key in list(self.cache.keys()):
            if key not in self.cache_durations:
                del self.cache[key]
                continue
            if self.cache_durations[key] < time.time():
                del self.cache[key]
                del self.cache_durations[key]
                os.remove(f"{self.folder}/{key}")
        self.save()
    def restore(self):
        self.load()
        self.cleanup()