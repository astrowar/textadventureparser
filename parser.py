
class SourceLocation:
    def __init__(self, line, column):
        self.line = line
        self.column = column

    def __repr__(self):
        return f"SourceLocation(line={self.line}, column={self.column})"


class ASTNode:
    def __init__(self, sourceLocation=None):
        self.sourceLocation = sourceLocation

class LiteralNode(ASTNode):
    def __init__(self, value, sourceLocation: SourceLocation):
        super().__init__(sourceLocation)
        self.value = value

    def __repr__(self):
        return f"Literal(value={self.value!r})"


class IdentifierNode(ASTNode):
    def __init__(self, value , sourceLocation: SourceLocation):
        super().__init__(sourceLocation)
        self.value = value


    def __repr__(self):
        return f"#[{self.value!r}]"
        #return f"Identifier(value={self.value!r}, location={self.sourceLocation!r})"


