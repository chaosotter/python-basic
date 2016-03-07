class Runtime:
    """Encapsulates the runtime state of execution itself, excluding I/O."""

    def __init__(self, program, env):
        self.program = program
        self.env = env
