def define_function(app):
    @app.get("/functions/greet")
    def greet(name: str):
        return f"Hello {name}"
