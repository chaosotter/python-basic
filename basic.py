import getopt
import select
import sys
import tty
import termios

from lib import parser
from lib import runtime
from lib import system
from lib import value

# The default command prompt.
PROMPT = 'READY'

class Basic:
    """Encapsulates the running state of the whole interpreter."""
    
    def __init__(self, input_mode='line'):
        self.input_mode = input_mode
        self.Boot()
        self.REPL()

    def Boot(self):
        # Initialize state.
        self.folder = 'default'  # current directory for file operations
        self.screen = system.Screen()  # tracks texels for full screen
        self.rt = runtime.Runtime(runtime.Program(), runtime.Environment())
        self.timer = None  # used in JS version

        # Display the initial splash screen.
        self.screen.WriteLn('Python BASIC Version 0.0.1')
        self.screen.WriteLn('Enjoy yourself and play nicely with others.')
        self.screen.WriteLn()
        self.screen.WriteLn('Using ', self.input_mode, ' input mode.')
        self.screen.WriteLn()
        self.screen.WriteLn(PROMPT)

    def KeyboardHasData(self, timeout=0):
        return select.select([sys.stdin], [], [], timeout) == ([sys.stdin], [], [])

    def REPL(self):
        """The basic Read-Eval-Print loop for the interpreter."""
        if self.input_mode == 'line':
            while True:
                line = raw_input('>')
                self.Execute(line)
        else:
            old_term = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                while True:
                    ch = self.KeyboardHasData(timeout=0.250)
                    if ch:
                        self.KeyPressed(ch)
                    else:
                        self.KeyReleased()
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term)
    
        self.screen.WriteLn('Good-bye.')

    def Execute(self, line):
        """Attempts to execute the code in a line of input.
        
        This is invoked by both the read-eval-print loop and the LOAD command,
        which basically simulates typing in the program from the REPL.
        
        Returns true if the execution was successful.
        """
        # Build a parser around the input.
        p = parser.Parser(parser.TokenStream(line))

        # Try to read and evaluate a statement.
        try:
            statement_set = p.read()
            if statement_set:
                for statement in statement_set.set:
                    statement.validate(self.rt).evaluate(self.rt)
            return True
        except Exception as e:
            self.screen.WriteLn(e)
            self.screen.WriteLn()
            return False

    def KeyPressed(self, ch):
        """Handles incoming key presses, which may trigger the parser."""
        # Update the INKEY$ variable.
        self.rt.env.Set('inkey$', value.VString(ch))
        
        # Send the key to the screen.
        line = self.screen.Send(ch)

        # If we have a complete line, execute it.
        if line is not None:
            self.Execute(line)

    def KeyReleased(self):
        """Called when we detect that a key is no longer being pressed."""
        # Update the INKEY$ variable.
        self.rt.env.Set('inkey$', value.VString(''))


def main(argv):
    """Main routine: parse command-line flags and start the REPL."""
    try:
        opts, args = getopt.getopt(argv, '', ['input_mode='])
    except getopt.GetoptError:
        print >>sys.stderr, 'basic --input_mode=(line|unbuffered)'
        sys.exit(1)

    mode = 'line'
    for opt, arg in opts:
        if opt == '--input_mode' and arg in ('line', 'unbuffered'):
            mode = arg

    state.basic = Basic(input_mode=mode)
    state.basic.Boot()


if __name__ == '__main__':
   main(sys.argv[1:])
