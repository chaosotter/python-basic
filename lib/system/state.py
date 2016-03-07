class State:
    """Global state for the interpreter.
    
    The existence of this class is unfortunate and makes it difficult to support
    multiple interpreters running within the same process.  This pattern should
    be ripped out and replaced by something more civilized.
    """

    folder = ''  # TODO(chaosotter): Initialize with CWD.
