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
