from tokens import Token, TokenType
from expr import (
    Expr,
    Binary,
    Unary,
    Literal,
    Grouping,
    Variable,
    Assign,
    Logical,
    Call,
    Get,
    Set,
    This,
    Super,
)
from stmt import (
    Stmt,
    Print,
    Expression,
    Var,
    Block,
    If,
    While,
    Function,
    Return,
    Class,
)
from typing import List
from loxerror import LoxErrors, LoxParseError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.had_error = False

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self.is_at_end():
            statement = self.declaration()
            if statement is not None:
                statements.append(statement)
        return statements

    def error(self, token: Token, message: str) -> LoxParseError:
        if token.token_type == TokenType.EOF:
            LoxErrors.report(token.line, " at end", message)
        else:
            LoxErrors.report(token.line, f" at '{token.lexeme}'", message)
        self.had_error = True
        return LoxParseError(token, message)

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            if self.peek().token_type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return
            self.advance()

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.SUPER):
            keyword: Token = self.previous()
            self.consume(TokenType.DOT, 'Expect "." after "super".')
            method: Token = self.consume(
                TokenType.IDENTIFIER, "Expect superclass method name."
            )
            return Super(keyword, method)
        if self.match(TokenType.THIS):
            return This(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        raise self.error(self.peek(), "Expect Expression.")

    def finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        paren: Token = self.consume(
            TokenType.RIGHT_PAREN, 'Expect ")" after arguments.'
        )
        return Call(callee, paren, arguments)

    def call(self) -> Expr:
        expr: Expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name: Token = self.consume(
                    TokenType.IDENTIFIER, 'Expect property name after ".".'
                )
                expr = Get(expr, name)
            else:
                break
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def and_func(self) -> Expr:
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr: Expr = Logical(expr, operator, right)

        return expr

    def or_func(self) -> Expr:
        expr: Expr = self.and_func()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.and_func()
            expr: Expr = Logical(expr, operator, right)

        return expr

    def assignment(self) -> Expr:
        expr: Expr = self.or_func()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            raise self.error(equals, "Invalid assignment target.")
        return expr

    def expression(self) -> Expr:
        return self.assignment()

    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        return self.expression_statement()

    def declaration(self) -> Stmt | None:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except LoxParseError:
            self.synchronize()
            return None

    def class_declaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass: Variable | None = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE, 'Expect "{" before class body.')
        methods: list[Function] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, 'Expect "}" after class body.')
        return Class(name, superclass, methods)

    def function(self, kind: str) -> Function:
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f'Expect "(" after {kind} name.')
        parameters: list[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters")

                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after parameters.')
        self.consume(TokenType.LEFT_BRACE, f'Expect "{{" before {kind} body.')
        body: list[Stmt] = self.block()
        return Function(name, parameters, body)

    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ";" after value.')
        return Print(value)

    def return_statement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ";" after return value.')
        return Return(keyword, value)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "while".')
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after condition.')
        body: Stmt = self.statement()
        return While(condition, body)

    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ";" after expression.')
        return Expression(expr)

    def var_declaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Expr | None = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ";" after variable declaration.')
        return Var(name, initializer)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt: Stmt | None = self.declaration()
            if stmt is not None:
                statements.append(stmt)

        self.consume(TokenType.RIGHT_BRACE, 'Expect "}" after block.')
        return statements

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "if".')
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after if condition.')

        then_branch: Stmt = self.statement()
        else_branch: Stmt | None = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "for".')
        if self.match(TokenType.SEMICOLON):
            initializer: Stmt | None = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition: Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ";" after loop condition.')
        increment: Expr | None = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after for clauses.')
        body = self.statement()
        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body
