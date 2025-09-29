from typing import Self

class Source:
    def __init__(self, text: str, name: str = "<stdin>"):
        self.text = text
        self.name = name
        
    @classmethod
    def from_path(cls, path: str) -> Self:
        with open(path, "r", encoding="utf-8") as f:
            return cls(f.read(), name=path)

    @classmethod
    def from_string(cls, text: str, name: str = "<string>") -> Self:
        """Create a Source from a provided string."""
        return cls(text, name=name)

    @classmethod
    def from_stdin(cls) -> Self:
        """Create a Source by reading all data from standard input."""
        import sys
        data = sys.stdin.read()
        return cls(data, name="<stdin>")

    def pos_to_line_col(self, pos: int) -> tuple[int, int]:
        """Convert a position in the source code to (line, col) tuple."""
        line = 1
        col = 1
        for i in range(pos):
            if self.text[i] == '\n':
                line += 1
                col = 1
            else:
                col += 1
        return line, col

    def get_line(self, line_number: int) -> str:
        """Return the content of a specific line (starting from 1)."""
        lines = self.text.splitlines()
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1]
        raise IndexError(f"Line {line_number} out of range (1-{len(lines)})")
    
    def __len__(self):
        """Return the length of the source text."""
        return len(self.text)
    
    def __getitem__(self, key):
        """Allow indexing into the source text."""
        return self.text[key]
    
    def __str__(self):
        """Return the string representation of the source text."""
        return self.text
