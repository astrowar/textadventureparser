import sys
import os
from typing import List, Union
from parser import ASTNode,  SourceLocation, LiteralNode, IdentifierNode
from syntax_template import match_template


def getLineOffsets( contents: str ) -> List[int]:
    linestart_offsets = []
    current_line = 1
    for i, char in enumerate(contents):
        if char == "\n":
            current_line += 1
            linestart_offsets.append((i, current_line))

    return linestart_offsets

def getLinenumber( linestart_offsets: List[int], offset: int ) -> Union[int, None]:
    for i in range(len(linestart_offsets) - 1):
        linestartOffset , linenumber = linestart_offsets[i]
        nextlinestartOffset, _ = linestart_offsets[i + 1]
        if linestartOffset <= offset < nextlinestartOffset:
            return linenumber
    if linestart_offsets and offset >= linestart_offsets[-1][0]:
        return linestart_offsets[-1][1]
    return None

def splitTermPunct( x: List[IdentifierNode]  ) -> List[IdentifierNode] :
    #for each term split .,?! etc e tal
    #"scenery."  -> ["scenery", "."]
    import re
    result = []
    punct_re = re.compile(r'(\w+|[^\w\s])') #match words or single punctuation
    for node in x:
        matches = punct_re.findall(node.value)
        offset = 0
        for match in matches:
            loc = SourceLocation(node.sourceLocation.line, node.sourceLocation.column + offset)
            result.append(IdentifierNode(match, loc))
            offset += len(match)
    return result

def splitTerm( x : IdentifierNode  ) -> List[IdentifierNode]:
    #value nas white spaces ?
    if   x.value.count(' ')  == 0:
        return [x]
    values_offset  = [] #store (offset, value)
    #use re to split by whitespace but keep the offsets
    import re
    for match in re.finditer(r'\S+', x.value):
        values_offset.append( (match.start(), match.group(0)) )
    result = []
    for offset, value in values_offset:
        loc = SourceLocation(x.sourceLocation.line, x.sourceLocation.column + offset)
        result.append(IdentifierNode(value, loc))
    result = splitTermPunct( result )
    return result


def splitTerms( nodes : List[ASTNode]  ) -> List[ASTNode]:
    result = []
    for node in nodes:
        if isinstance(node, IdentifierNode):
            result.extend(splitTerm(node))
        else:
            result.append(node)
    return result

def splitLines( file: str, contents: str ) -> List[ASTNode]:
    lines =  []
    pivot = 0
    is_literal = False
    line_num = 1
    collumn_ofset = 0
    for i, c in enumerate(contents):
        if (c == '\n'):
            if not is_literal:
                # unterminated literal
                loc = SourceLocation(line_num, pivot - collumn_ofset  )
                lines.append(IdentifierNode(contents[pivot:i], loc))
                pivot = i + 1  # next char
            else:  # unterminated literal
                # all literals are multiline
                pass
            line_num += 1
            collumn_ofset = i+1

        if c == '"':  # start a literal?
            #store any previous identifier
            if not is_literal:
                loc = SourceLocation(line_num, pivot - collumn_ofset )
                lines.append(IdentifierNode(contents[pivot:i], loc))

            if is_literal:
                is_literal = False
                loc = SourceLocation(line_num, pivot - collumn_ofset )
                lines.append(LiteralNode(contents[pivot:i + 1], loc))
                pivot = i + 1  # next char
            else:
                pivot = i
                is_literal = True
    if pivot < len(contents):
        loc = SourceLocation(line_num,   pivot - collumn_ofset )
        if is_literal:
            lines.append(LiteralNode(contents[pivot:], loc))
        else:
            lines.append(IdentifierNode(contents[pivot:], loc))

    #remove all IdentifierNodes that are just whitespace
    lines = [line for line in lines if not (isinstance(line, IdentifierNode) and line.value.strip() == "")]
    lines = splitTerms( lines )
    return lines




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <scriptfile>")
        sys.exit(1)

    scriptfile = sys.argv[1]
    contents = ""
    with open(scriptfile, 'r') as f:
        contents = f.read()

    lines = splitLines(scriptfile, contents)
    #group same line
    grouped_lines = {} #line number , ids from this line
    for node in lines:
        if node.sourceLocation.line not in grouped_lines:
            grouped_lines[node.sourceLocation.line] = []
        grouped_lines[node.sourceLocation.line].append(node)

    for line_num in sorted(grouped_lines.keys()):
        print(f"Line {line_num}:")
        for node in grouped_lines[line_num]:
            print(f"  {node}")

    templates =  match_template(lines )
    for t in templates:
        print(t)
