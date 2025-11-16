from .token import Token, TokenType
from .node import Node, NodeType
from .source import Source

from .lexer import Lexer

from .utils.errors import CompilationError
from .utils.logger import Logger

class Parser:

    def __init__(self, lexer: Lexer, source_code: Source = None, verbose: bool = False):
        self.lexer = lexer or Lexer(source_code, verbose)
        self.source_code = source_code
        self.verbose = verbose

    def parse(self) -> Node:
        """Entry point"""
        if self.lexer.T is None or self.lexer.T.type == TokenType.TOK_EOF:
            return None

        N: Node = self.F()
        if self.verbose:
            Logger.log("Syntax analysis / Parsing (AST):")
            N.print(mode="beautify")

        return N

    def F(self) -> Node:
        """Parse one function definition"""
        self.lexer.accept(TokenType.TOK_INT)
        self.lexer.accept(TokenType.TOK_IDENT)
        func_name = self.lexer.T_prev.repr

        func_node = Node(NodeType.NODE_FUNCTION, repr=func_name, children=[])

        self.lexer.accept(TokenType.TOK_LPARENTHESIS)
        if not self.lexer.check(TokenType.TOK_RPARENTHESIS):
            func_node.children.extend(self._parse_function_parameters())
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)

        body = self.I()
        func_node.add_child(body)
        return func_node

    def _parse_function_parameters(self) -> list[Node]:
        params: list[Node] = []
        while True:
            self.lexer.accept(TokenType.TOK_INT)
            while self.lexer.check(TokenType.TOK_MUL):
                pass
            self.lexer.accept(TokenType.TOK_IDENT)
            ident = self.lexer.T_prev.repr
            params.append(Node(NodeType.NODE_DECLARE, repr=ident))
            if not self.lexer.check(TokenType.TOK_COMMA):
                break
        return params

    # Grammar implementation
    def E(self, prio: int = 0) -> Node:
        """Parse binary operations expressions"""
        N: Node = self.P()  # first argument

        # continue parsing binary operations as long as the next token is a binary operator with right priority
        while self.lexer.T and self.lexer.T.type in Node.OP:
            op_tok = self.lexer.T.type
            if Node.OP[op_tok]["prio"] < prio:
                break  # priority filter
            self.lexer.next()
            M = self.E(
                Node.OP[op_tok]["prio_arg"]
            )  # second argument (can be another expression)
            N: Node = Node(Node.OP[op_tok]["ntype"], children=[N, M])

        return N

    def A(self) -> Node:
        """Parse atomic expressions"""
        # A -> nb | (E)
        # number
        if self.lexer.check(TokenType.TOK_CONST):
            # The value is on T_prev after advancing
            value = self.lexer.T_prev.value
            return Node(NodeType.NODE_CONST, value=value, children=[])

        # (E)
        if self.lexer.check(TokenType.TOK_LPARENTHESIS):
            r = self.E()
            # require )
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)
            return r

        # <id>
        if self.lexer.check(TokenType.TOK_IDENT):
            return Node(NodeType.NODE_REF, repr=self.lexer.T_prev.repr)

        # error
        line, col = self.lexer.source_code.pos_to_line_col(self.lexer.pos)
        raise CompilationError(
            f"Unexpected token {self.lexer.T.repr!r} at line {line}, column {col}: expected constant or '('"
        )

    def P(self) -> Node:
        """Parse expressions with unary prefix operators"""
        # P -> !P | -P | +P | S
        if self.lexer.check(TokenType.TOK_MUL):
            return Node(NodeType.NODE_DEREF, children=[self.P()])
        if self.lexer.check(TokenType.TOK_ADDRESS):
            return Node(NodeType.NODE_ADDRESS, children=[self.P()])
        if self.lexer.check(TokenType.TOK_NOT):
            # [not]->[P]
            return Node(NodeType.NODE_NOT, children=[self.P()])
        elif self.lexer.check(TokenType.TOK_SUB):
            # [neg]->[P]
            return Node(NodeType.NODE_NEG, children=[self.P()])
        elif self.lexer.check(TokenType.TOK_ADD):
            # +P => P
            return self.P()
        # default: S
        return self.S()

    def S(self) -> Node:
        """Parse expressions with unary suffix operators"""
        node = self.A()
        while True:
            if self.lexer.check(TokenType.TOK_LPARENTHESIS):
                args = self._parse_call_arguments()
                node = Node(NodeType.NODE_CALL, children=[node, *args])
                continue
            if self.lexer.check(TokenType.TOK_LBRACKET):
                base = node
                index_expr = self.E()
                self.lexer.accept(TokenType.TOK_RBRACKET)
                plus = Node(NodeType.NODE_ADD, children=[base, index_expr])
                node = Node(NodeType.NODE_DEREF, children=[plus])
                continue
            if self.lexer.check(TokenType.TOK_INC):
                node = self._make_inc_dec_node(node, delta=1)
                continue
            if self.lexer.check(TokenType.TOK_DEC):
                node = self._make_inc_dec_node(node, delta=-1)
                continue
            break
        return node

    def _parse_call_arguments(self) -> list[Node]:
        """Helper to parse function call arguments"""
        args: list[Node] = []
        if self.lexer.check(TokenType.TOK_RPARENTHESIS):
            return args
        while True:
            args.append(self.E())
            if self.lexer.check(TokenType.TOK_COMMA):
                continue
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)
            break
        return args

    def I(self) -> Node:
        """Parse an instruction ("expr;", block or debug)"""
        # debug E ;
        if self.lexer.check(TokenType.TOK_DEBUG):
            N: Node = self.E()
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return Node(NodeType.NODE_DEBUG, children=[N])

        # { I* }
        if self.lexer.check(TokenType.TOK_LBRACE):
            block = Node(NodeType.NODE_BLOCK, children=[])
            while not self.lexer.check(TokenType.TOK_RBRACE):
                block.add_child(self.I())
            return block

        # while (E) I
        if self.lexer.check(TokenType.TOK_WHILE):
            loop = Node(NodeType.NODE_LOOP, children=[Node(NodeType.NODE_TARGET, value=False, children=[])])
            self.lexer.accept(TokenType.TOK_LPARENTHESIS)
            cond_expr = self.E()
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)
            body = self.I()
            cond = Node(NodeType.NODE_COND, children=[cond_expr, body, Node(NodeType.NODE_BREAK, children=[])])
            loop.add_child(cond)
            return loop

        # do I while (E);
        if self.lexer.check(TokenType.TOK_DO):
            body = self.I()
            target = Node(NodeType.NODE_TARGET, value=True, children=[])
            self.lexer.accept(TokenType.TOK_WHILE)
            self.lexer.accept(TokenType.TOK_LPARENTHESIS)
            cond_expr = self.E()
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)
            self.lexer.accept(TokenType.TOK_SEMICOLON)

            negated = Node(NodeType.NODE_NOT, children=[cond_expr])
            cond = Node(NodeType.NODE_COND, children=[negated, Node(NodeType.NODE_BREAK, children=[])])

            return Node(NodeType.NODE_LOOP, children=[body, target, cond])

        # for (E1; E2; E3) I
        if self.lexer.check(TokenType.TOK_FOR):
            self.lexer.accept(TokenType.TOK_LPARENTHESIS)

            init_node = None
            if self.lexer.T.type != TokenType.TOK_SEMICOLON:
                init_node = self._parse_for_initializer()
            self.lexer.accept(TokenType.TOK_SEMICOLON)

            cond_expr = None
            if self.lexer.T.type != TokenType.TOK_SEMICOLON:
                cond_expr = self.E()
            self.lexer.accept(TokenType.TOK_SEMICOLON)

            step_expr = None
            if self.lexer.T.type != TokenType.TOK_RPARENTHESIS:
                step_expr = self.E()
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)

            body = self.I()

            if cond_expr is None:
                cond_node = Node(NodeType.NODE_CONST, value=1, children=[])
            else:
                cond_node = cond_expr

            target = Node(NodeType.NODE_TARGET, value=True, children=[])
            seq_children = [body, target]
            if step_expr is not None:
                seq_children.append(Node(NodeType.NODE_DROP, children=[step_expr]))
            seq = Node(NodeType.NODE_SEQ, children=seq_children)

            cond = Node(
                NodeType.NODE_COND,
                children=[cond_node, seq, Node(NodeType.NODE_BREAK, children=[])],
            )

            loop = Node(NodeType.NODE_LOOP, children=[cond])

            nodes = []
            if init_node is not None:
                nodes.append(init_node)
            nodes.append(loop)

            if len(nodes) == 1:
                return nodes[0]
            return Node(NodeType.NODE_SEQ, children=nodes)

        # if (E) I [else I]?
        if self.lexer.check(TokenType.TOK_IF):
            N: Node = Node(NodeType.NODE_COND)

            # evaluate condition
            self.lexer.accept(TokenType.TOK_LPARENTHESIS)
            cond = self.E()
            N.add_child(cond)
            self.lexer.accept(TokenType.TOK_RPARENTHESIS)

            # then instruction
            then_instr = self.I()
            N.add_child(then_instr)

            # (optional) else instruction
            if self.lexer.check(TokenType.TOK_ELSE):
                N.add_child(self.I())
            
            return N

        # int <id> ; (declaration)
        if self.lexer.check(TokenType.TOK_INT):
            while self.lexer.check(TokenType.TOK_MUL):
                pass
            self.lexer.accept(TokenType.TOK_IDENT)
            ident = self.lexer.T_prev.repr
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return Node(NodeType.NODE_DECLARE, repr=ident)

        # break ;
        if self.lexer.check(TokenType.TOK_BREAK):
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return Node(NodeType.NODE_BREAK)

        # continue ;
        if self.lexer.check(TokenType.TOK_CONTINUE):
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return Node(NodeType.NODE_CONTINUE)

        # return E;
        if self.lexer.check(TokenType.TOK_RETURN):
            expr = self.E()
            self.lexer.accept(TokenType.TOK_SEMICOLON)
            return Node(NodeType.NODE_RETURN, children=[expr])

        # E ;  => drop
        N: Node = self.E()
        self.lexer.accept(TokenType.TOK_SEMICOLON)
        return Node(NodeType.NODE_DROP, children=[N])

    def _make_inc_dec_node(self, node: Node, delta: int) -> Node:
        """Helper to create increment/decrement nodes"""
        if node.type != NodeType.NODE_REF:
            line, col = self.lexer.source_code.pos_to_line_col(self.lexer.pos)
            op = "++" if delta > 0 else "--"
            raise CompilationError(
                f"Operator {op} requires an identifier at line {line}, column {col}"
            )

        ident = node.repr
        ref_lhs = Node(NodeType.NODE_REF, repr=ident)
        ref_rhs = Node(NodeType.NODE_REF, repr=ident)
        delta_node = Node(NodeType.NODE_CONST, value=abs(delta), children=[])

        if delta > 0:
            updated_value = Node(NodeType.NODE_ADD, children=[ref_rhs, delta_node])
        else:
            updated_value = Node(NodeType.NODE_SUB, children=[ref_rhs, delta_node])

        return Node(NodeType.NODE_AFFECT, children=[ref_lhs, updated_value])

    def _parse_for_initializer(self) -> Node:
        """Helper to parse for loop initializer (declaration or expression)"""
        if self.lexer.T.type == TokenType.TOK_INT:
            self.lexer.accept(TokenType.TOK_INT)
            while self.lexer.check(TokenType.TOK_MUL):
                pass
            self.lexer.accept(TokenType.TOK_IDENT)
            ident = self.lexer.T_prev.repr
            decl = Node(NodeType.NODE_DECLARE, repr=ident)
            children = [decl]

            if self.lexer.check(TokenType.TOK_AFFECT):
                expr = self.E()
                assign = Node(
                    NodeType.NODE_AFFECT,
                    children=[Node(NodeType.NODE_REF, repr=ident), expr],
                )
                children.append(Node(NodeType.NODE_DROP, children=[assign]))

            if len(children) == 1:
                return children[0]
            return Node(NodeType.NODE_SEQ, children=children)

        expr = self.E()
        return Node(NodeType.NODE_DROP, children=[expr])
