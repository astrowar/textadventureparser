import sys
import os
from typing import List, Union
from emit import Program
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
    punct = set(['.',',','!','?',';',':'])
    #value nas white spaces ?
    
    terms_out = []  #( offset , string)
    remainder = x.value+""
    i = 0
    offset = 0
    while len(remainder) > 0 :
        if remainder[i] == ' ' :
            # an this -> +[an] remainder:[this]
            terms_out .append( ( offset,remainder[ :i]))
            remainder = remainder[i+1:]
            offset += i + 1
            i = 0   
        elif remainder[i] in punct :
            # an.this -> +[an] +[.] remainder:[this]
            terms_out.append( ( offset,remainder[ :i]))
            terms_out.append( ( offset + i, remainder[i] + "") )
            remainder = remainder[i+1:]
            offset += i + 1
            i = 0    
        else:
            i += 1
            if i >= len(remainder):
                terms_out.append( ( offset,remainder))
                remainder = ""
                i = 0
                break 
            
    terms_out= [ (t[0], t[1].strip()) for t in terms_out ]        
    terms_out = [ t for t in terms_out if t[1] != ""  ]        
 
    result = []
    for term in terms_out:
        loc = SourceLocation(x.sourceLocation.line, x.sourceLocation.column + term[0])
        result.append(IdentifierNode(term[1], loc))
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


def emit_program( scriptfile: str ):
    prog = Program()
    with open(scriptfile, 'r') as f:
        contents = f.read()
    lines = splitLines(scriptfile, contents)
    
         
    templates =  match_template(lines )

    for tlist in templates:
        for t in tlist:
            print(f"Emitting template: {t}")
            errorCode = prog.emit(t)
            if errorCode:
                return prog, errorCode
    prog.initVars()        
    return prog, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <scriptfile>")
        sys.exit(1)

    scriptfile = sys.argv[1]
    contents = ""

    p = emit_program(scriptfile)
    prog, errorCode = p
    if errorCode:
        print(f"Error emitting program: {errorCode}")
    else:
        print("Program emitted successfully.")
        for instances in prog.instances:
            print(f"Instance: {instances.name}")
            for var in instances.kindVariables.values():
                print(f"  Variable: {var.name}, Initial Value: {var.initial_value}")
            for enumVar in instances.enumVariables.values():
                print(f"  Enum Variable: {enumVar.options}, Initial Value: {enumVar.initial_value}")    
        for kinds in prog.kinds:
            print(f"Kind: {kinds.name}")
            for var in kinds.kindVariables.values():
                print(f"  Variable: {var.name}, Initial Value: {var.initial_value}")
            for enumVar in kinds.enumVariables.values():
                print(f"  Enum Variable: {enumVar.options}, Initial Value: {enumVar.initial_value}")

     
        
