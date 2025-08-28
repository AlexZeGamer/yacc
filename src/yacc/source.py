from typing import Self

class Source:
    def __init__(self, text: str, name: str = "<stdin>"):
        self.text = text
        self.name = name
        
    @classmethod
    def from_path(cls, path: str) -> Self:
        with open(path, "r", encoding="utf-8") as f:
            return cls(f.read(), name=path)

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
    
    def __len__(self):
        """Return the length of the source text."""
        return len(self.text)
    
    def __getitem__(self, key):
        """Allow indexing into the source text."""
        return self.text[key]
    
    def __str__(self):
        """Return the string representation of the source text."""
        return self.text
