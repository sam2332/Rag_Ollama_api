
def digest_str_duration(s):
    #1h, 1d, 24m, 60s
    if s[-1] == "h":
        return int(s[:-1])*60*60
    if s[-1] == "d":
        return int(s[:-1])*60*60*24
    if s[-1] == "m":
        return int(s[:-1])*60
    if s[-1] == "s":
        return int(s[:-1])
    return 0
    



from Libs.RequestSchema import ChatPassthroughRequest
import json
import hashlib
def hash_ChatPassthroughRequest(data: ChatPassthroughRequest):
    data = json.dumps({
        "model": data.model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in data.messages],
        "options": { 
            "temperature": data.temperature,
        },
    })
    #md5
    return hashlib.md5(data.encode()).hexdigest()





import jsonpickle
def hash_anything(o):
    data = jsonpickle.encode(o)
    return hashlib.md5(data.encode()).hexdigest()




def make_embeddings_safe_for_db(embedding):
    return str(embedding).replace('[', '{').replace(']', '}')
