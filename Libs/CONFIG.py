from Libs.ConfigFile import ConfigFile


def get_config():
    config = ConfigFile("config.json")
    if not config.load():
        config.set("chat_model", "llama3:latest")
        config.set("embeddings_model", "mxbai-embed-large")
        config.set("config.get('ollama_host')", "http://localhost:11434")
        config.set("embeddings_model_db", "default")
        config.save()
    return config
