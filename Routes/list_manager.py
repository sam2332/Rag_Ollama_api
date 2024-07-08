from pydantic import BaseModel
from Libs.DB import ListManager


def register_routes(app):
    @app.get("/lists/{list_name}", tags=["lists"])
    def get_list_contents(list_name: str):
        manager = ListManager()
        return manager.get_list_items(list_name)

    class ListManagerAddItemRequest(BaseModel):
        source: str
        content: str
        tags: str
        _unique: bool = True

    @app.post("/lists/{list_name}", tags=["lists"])
    def add_list_item(list_name: str, data: ListManagerAddItemRequest):
        manager = ListManager()
        manager.add_list_item(
            list_name, data.source, data.content, data.tags, _unique=data._unique
        )
        return {"status": "ok"}

    @app.delete("/lists/{list_name}", tags=["lists"])
    def delete_list(list_name: str):
        manager = ListManager()
        manager.delete_list(list_name)
        return {"status": "ok"}

    @app.get("/lists", tags=["lists"])
    def list_lists():
        manager = ListManager()
        return manager.list_lists()
