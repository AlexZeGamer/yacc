import sys

class Logger:
    @staticmethod
    def log(message: str) -> None:
        """
        Log a message (for verbose/debug mode)
        to stderr to avoid mixing with normal stdout output
        (e.g. for piping assembly code to the simulator).
        """
        print(message, file=sys.stderr)
