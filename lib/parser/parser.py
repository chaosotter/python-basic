class Parser:
    """Recursive-descent parser for BASIC statements and expressions."""

    def __init__(self, stream):
        self.stream = stream

