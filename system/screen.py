import sys

class Screen:
    """Abstracts over the notion of a terminal-based output display."""

    def __init__(self):
        pass

    def WriteLn(self, *args):
        for arg in args:
            sys.stdout.write(str(arg))
        sys.stdout.write('\n')
