from typing import List

from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

import os


import ast
import operator


@tool
def math(expr):
    """
    Safely evaluates a mathematical expression.

    Args:
        expr: string expression of math problem

    Returns:
        Result of the evaluated expression as a float.
    """
    # Supported operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
    }

    def eval_(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](eval_(node.left), eval_(node.right))
        else:
            raise TypeError(node)

    node = ast.parse(expr, mode="eval").body
    return eval_(node)


if os.path.exists("Jail_FS") == False:
    os.mkdir("Jail_FS")


# filesystem tools write,read,delete,list from jail folder called Jail_FS
@tool
def write(file_name, content):
    """
    Write content to a file.

    Args:
        file_name: Name of the file to write to.
        content: Content to write to the file.

    Returns:
        None
    """
    with open(f"Jail_FS/{file_name}", "w") as f:
        f.write(content)


@tool
def read(file_name):
    """
    Read content from a file.

    Args:
        file_name: Name of the file to read from.

    Returns:
        Content of the file.
    """
    with open(f"Jail_FS/{file_name}", "r") as f:
        return f.read()


@tool
def delete(file_name):
    """
    Delete a file.

    Args:
        file_name: Name of the file to delete.

    Returns:
        None
    """
    os.remove(f"Jail_FS/{file_name}")


@tool
def list_files():
    """
    List all files in the jail folder.

    Args:
        None

    Returns:
        List of all files in the jail folder.
    """
    return os.listdir("Jail_FS")


@tool
def run_python_file(file_name):
    """
    Run a python file.

    Args:
        file_name: Name of the file to run.

    Returns:
        None
    """
    with open(f"Jail_FS/{file_name}", "r") as f:
        sg = PySimpleGUI.PySimpleGUI()
        code = f.read()
        # show user the code that is going to be run
        layout = [
            [sg.Text("Code that will be run:")],
            [sg.Multiline(code, size=(100, 10))],
            [sg.Button("Run"), sg.Button("Cancel")],
        ]
        window = sg.Window("Run Python File", layout)
        event, values = window.read()
        window.close()
        if event == "Run":
            exec(code)
        else:
            return "Cancelled"
    return "Success"


llm = ChatOllama(
    model=os.environ.get("langchain_tool_model"),
    temperature=0.3,
    num_ctx=4096,
)
tools = [math, write, read, delete, list_files, run_python_file]
tool_cbs = {t.func.__name__.lower(): t for t in tools}
llm_with_tools = llm.bind_tools(tools)


def register_routes(app):
    @app.get("/langchain/query", tags=["langchain"])
    def query_langchain(query: str):
        messages = [
            SystemMessage(
                "Please provide the information that is requested. Use tools before your own information if possible"
            ),
            HumanMessage(query),
        ]
        ai_msg = llm_with_tools.invoke(query)
        messages.append(ai_msg)
        while len(ai_msg.tool_calls) > 0:
            for tool_call in ai_msg.tool_calls:
                selected_tool = tool_cbs[tool_call["name"].lower()]
                tool_output = selected_tool.invoke(tool_call["args"])
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            ai_msg = llm.invoke(messages)
            messages.append(ai_msg)
        return messages
