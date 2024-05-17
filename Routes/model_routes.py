from Libs.model_helper import check_model_exists, list_available_models


def register_routes(app):
    # seperate set functionf for embedding_model and chat_model
    @app.post("/api/change_chat_model/")
    async def change_chat_model(data: ChangeEmbeddingDBFilename):
        if check_model_exists(data.name):
            app.config.set("chat_model", data.name)
            app.config.save()
            return {"status": "success"}
        return {
            "status": "error",
            "message": "Model does not exist",
            "available_models": list_available_models(),
        }

    @app.post("/api/change_embedding_model/")
    async def change_embedding_model(data: ChangeEmbeddingDBFilename):
        if check_model_exists(data.name):
            app.config.set("embeddings_model", data.name)
            app.config.save()
            return {"status": "success"}
        return {
            "status": "error",
            "message": "Model does not exist",
            "available_models": list_available_models(),
        }
