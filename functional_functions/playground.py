def define_function(app):
    @app.get("/functions/greet")
    def greet(name: str):
        return f"Hello {name}"

    @app.get("/functions/showpysimplegui")
    def show():
        # show pysimplegui
        from PySimpleGUI import PySimpleGUI as sg

        # ui asks for text and returns it
        layout = [[sg.Text("Enter your name")], [sg.InputText()], [sg.Button("Ok")]]
        window = sg.Window("Get name", layout)
        event, values = window.read()
        window.close()
        return values[0]
