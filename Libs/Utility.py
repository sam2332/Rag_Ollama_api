def digest_str_duration(s):
    # 1h, 1d, 24m, 60s
    if s[-1] == "h":
        return int(s[:-1]) * 60 * 60
    if s[-1] == "d":
        return int(s[:-1]) * 60 * 60 * 24
    if s[-1] == "m":
        return int(s[:-1]) * 60
    if s[-1] == "s":
        return int(s[:-1])
    return 0


from Libs.RequestSchema import ChatPassthroughRequest
import json
import hashlib


import jsonpickle


def hash_anything(o):
    data = jsonpickle.encode(o)
    return hashlib.md5(data.encode()).hexdigest()


import jsonpickle
import os
import requests

# function to cache data in incrementing files
cache_first_run = True


def data_spy(data, cache_dir):
    if not os.path.exists(cache_dir):
        return
    global cache_first_run
    if cache_first_run:
        cache_first_run = False
        for file in os.listdir(cache_dir):
            os.remove(f"{cache_dir}/{file}")
    cache_file = f"{cache_dir}/{len(os.listdir(cache_dir))}.txt"
    with open(cache_file, "w") as f:
        f.write(jsonpickle.encode(data, unpicklable=False).replace("\\n", "\n"))
    return cache_file
