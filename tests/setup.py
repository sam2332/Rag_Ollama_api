def setupUnitTest():
    import sys
    import os
    if not os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) in sys.path:
        # Add the project root directory to the sys.path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
