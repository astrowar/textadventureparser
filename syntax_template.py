import os
from typing import List, Union , Dict, Any , Generator
from parser import ASTNode,  SourceLocation, LiteralNode, IdentifierNode
from emit import INSTANCE, CVAR_ENUM, CVAR_KIND, INITIAL_ASSIGN, SUBCLASS

#Language Instructions
    #CreateAssert( X , "property" , Y )
    #createInstance( X , Y )
    #createSubClass( X , Y )

 


#---------------------------------

def generateCombinations( parts:  List[Any] , n: int )  :
    #this method generate (yield) all combinations taking one element from each part group, total of N parts
    # [a,b,c,d], n=3 -> [[a,b][c][d]] , [[a][b,b][d]], [[a][b][c,d]]
    if n > len(parts)  or n <= 0:
        return
    if n == len(parts):
        yield [ [part] for part in parts ]
        return
    if n == 1:
        yield [parts]
    else:
        for i in range(1,len(parts)):
            first_part = parts[:i]
            for remaining_parts in generateCombinations(parts[i:], n-1):
                yield [first_part] + remaining_parts

def isValueEquivalent( a: str, b: str  ) -> bool:
    # b can be an string single, or an OR match kind  like : a/an/the 
    a = a.lower().strip()
    b = b.lower().strip()
    if "/" in b:
        options = [ opt.strip() for opt in b.split("/") ]
        for opt in options:
            if isValueEquivalent( a , opt ):
                return True
        return False
    return a == b

def match(  x:List[ASTNode] , template  )  :
    #split template by spaces
    template_parts = template.split(" ")
    for rr in generateCombinations( x , len(template_parts) ):
        match_vars = {}
        hasMatch = True
        for rrx, rrt in zip( rr , template_parts ):
            #print( "RR" , rrx , rrt)
            #rrx is a list of ASTNode
            #rrxt is a template part
            if rrt.startswith( "X")  or rrt.startswith("Y")  or rrt.startswith("Z") :
                #variable part
                match_vars[rrt] = rrx
            else:
                #fixed part
                #rrx must be a single IdentifierNode with value == rrt
                if len(rrx) != 1:
                    hasMatch = False
                    break
                node = rrx[0]
                if not isinstance(node, IdentifierNode):
                    hasMatch = False
                    break
                 
                if not isValueEquivalent(node.value, rrt):
                    #print(">>>", node.value , "!=" , rrt)
                    hasMatch = False
                    break
        if hasMatch:
            return match_vars
    return None

def decomposeOptions(x:List[ASTNode]):
    # a, b,c c or d  -> [a,b,c,d]
    # a or b -> [a,b]
    #a,b -> [a,b]
    options = []
    current_option = []
    for node in x:
        if isinstance(node, IdentifierNode):
            if node.value == ",":
                if current_option:
                    options.append( current_option )
                    current_option = []
            elif node.value == "or":
                if current_option:
                    options.append( current_option )
                    current_option = []
            else:
                current_option.append( node )
        else:
            current_option.append( node )
    if current_option:
        options.append( current_option )
    return options
    



def m_definition(x:List[ASTNode])   :
    # X is an Y called Z
    if mm := match( x,  "X is an/a kind of Y ."  ):
        return [  ( SUBCLASS ,  mm["X"], mm["Y"] ) ]   
    if mm := match( x,  "X is a/an kind ."  ):     
        return [  ( SUBCLASS ,  mm["X"], None ) ]
    if mm := match( x,  "X is a/an Y called Z ."  ):
        return [  ( INSTANCE ,  mm["X"], mm["Y"] ) ,  ( INITIAL_ASSIGN,  mm["X"] , "name" , mm["Z"] ) ]
    if mm := match( x,  "X is a/an Y ."  ):
        return [  ( INSTANCE ,  mm["X"], mm["Y"] ) ]
    if mm := match( x,  "X can be Y ."  ):
        options = decomposeOptions( mm["Y"] )
        return [  ( CVAR_ENUM ,  mm["X"],options ) ]

    if mm := match( x,  "X has a/an Y called Z ."  ):
        return [  ( CVAR_KIND ,  mm["X"], mm["Y"], mm["Z"] ) ]

    if mm := match( x,  "X is usually Y ."  ):
        return [  ( INITIAL_ASSIGN ,  mm["X"], mm["Y"] ) ]
        
    if mm := match( x,  "X is Y ."  ):
        return [  ( INITIAL_ASSIGN ,  mm["X"], mm["Y"] ) ]


def getTemplateMatch(x:List[ASTNode]):
    if mm := m_definition(x):
        return mm
    return None


def isEndPoint(x: ASTNode) :
    #is IdentifierNode and value is "."
    if isinstance(x, IdentifierNode):
        if x.value == ".":
            return True
    return False

def groupBy(x:List[Any], predicate)   :
    for i in range(len(x)):
        if predicate(x[i]):
            yield x[:i+1]
            yield from groupBy(x[i+1:], predicate)
            return

def match_template(x:List[ASTNode]) :
    #group by dot [.] terms
    for xgroup  in groupBy(x, isEndPoint):
        print("XGROUP:", xgroup)
        if mm := m_definition(xgroup):
            yield mm


if __name__ == "__main__":
    for g in  generateCombinations( "a b c e".split() , 2):
        print(g)

    x = "x y z . ab . D e ."
    x = x.split(" ")
    for group in groupBy(x, lambda v: v == "."):
        print("GROUP:", group)
