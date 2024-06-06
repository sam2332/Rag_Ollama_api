import requests


def check_model_exists(model_name):
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        models = response.json()["models"]
        for model in models:
            if model["name"] == model_name:
                return True
    return False


def list_available_models():
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        return response.json()["models"]
    return []


def pull_model(model_name):
    response = requests.post(
        "http://localhost:11434/api/pull", json={"model": model_name}
    )
    return response.status_code == 200
