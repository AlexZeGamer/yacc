class Symbol:
    def __init__(self, name: str, index: int = None):
        self.name: str = name
        self.index: int = index

class SymbolTable:
    def __init__(self):
        self.nbVars: int = 0
        self.scopes = []
    
    @property
    def current_scope(self):
        return self.scopes[-1] if self.scopes else None

    def start_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()
    
    def declare(self, name: str) -> Symbol:
        if name in self.current_scope:
            raise ValueError(f"Symbol {name} already declared in current scope")
        symbol = Symbol(name)
        self.current_scope[name] = symbol
        symbol.index = self.nbVars
        self.nbVars += 1
        return symbol
    
    def find(self, name: str) -> Symbol:
        for scope in self.scopes[::-1]:
            if name in scope:
                return scope[name]
        raise ValueError(f"Symbol {name} not found in any scope")
        