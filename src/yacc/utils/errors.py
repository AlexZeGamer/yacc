import sys

class CompilationError(Exception):
    """Base class for compiler-related errors."""
    def __init__(self, message: str, line: int=None, col: int=None, col_end: int=None, line_str: str=None) -> None:
        sys.excepthook = silent_hook # silent traceback for this error type

        self.message = message
        self.line = line
        self.col = col
        self.col_end = col_end
        self.line_str = line_str
        super().__init__(message)

    def __str__(self):
        """
        Print the error message in red.

        Example:
        ```
        Compilation Error:
          Division by zero (at line 10, col 12)
            x = 42 / 0
                   ^^^
        ```
        """
        error_message = f"Compilation Error:\n  {self.message}"

        # if we have line and column info, add it to the message
        if self.line is not None and self.col is not None:
            error_message += f" (at line {self.line}, col {self.col})"

            # if we have the line string, print it
            if self.line_str is not None:
                line_str_stripped = self.line_str.lstrip()
                shift = len(self.line_str) - len(line_str_stripped)
                error_message += f"\n    {line_str_stripped}"

                # underline the error position with carets (^)
                if self.col_end is not None and self.col_end > self.col:
                    error_message += "\n    " + " " * (self.col - 1 - shift) + "^" * (self.col_end - self.col)
                else:
                    error_message += "\n    " + " " * (self.col - 1 - shift) + "^"

        return f"\033[31m{error_message}\033[0m"

def silent_hook(exc_type, exc, tb):
    if issubclass(exc_type, CompilationError):
        print(exc, file=sys.stderr) # print only the error message, without traceback
    else:
        sys.__excepthook__(exc_type, exc, tb)

if __name__ == "__main__":
    raise CompilationError("Division by zero", line=10, col=12, col_end=15, line_str="    x = 42 / 0")
