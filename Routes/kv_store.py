from Libs.DB import KV_Store
from fastapi import Request
from pydantic import BaseModel


class KV_SET_REQUEST_MODEL(BaseModel):
    value: str


def register_routes(app):
    @app.get("/kvstore/{key}", tags=["kv_store"])
    def get_key(key: str):
        storage = KV_Store()
        return storage.get(key)

    @app.post("/kvstore/{key}", tags=["kv_store"])
    def set_key(key: str, request: KV_SET_REQUEST_MODEL):
        storage = KV_Store()
        value = request.value
        storage.set(key, value)
        return {"status": "ok"}

    @app.delete("/kvstore/{key}", tags=["kv_store"])
    def delete_key(key: str):
        storage = KV_Store()
        storage.delete(key)
        return {"status": "ok"}

    @app.get("/kvstore", tags=["kv_store"])
    def list_keys():
        storage = KV_Store()
        return storage.list()
