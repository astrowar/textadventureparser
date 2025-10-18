import os
from typing import List, Union , Dict, Any , Generator
from parser import ASTNode,  SourceLocation, LiteralNode, IdentifierNode

#Language Instructions
    #CreateAssert( X , "property" , Y )
    #createInstance( X , Y )
    #createSubClass( X , Y )

INSTANCE = "CreateInstance"
ASSIGN   = "CreateAssert"
SUBCLASS = "CreateSubClass"


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
                if node.value != rrt:
                    #print(">>>", node.value , "!=" , rrt)
                    hasMatch = False
                    break
        if hasMatch:
            return match_vars
    return None



def m_definition(x:List[ASTNode])   :
    # X is an Y called Z
    if mm := match( x,  "X is an Y called Z ."  ):
        return [  ( INSTANCE ,  mm["X"], mm["Y"] ) ,  ( ASSIGN,  mm["X"] , "name" , mm["Z"] ) ]
    if mm := match( x,  "X is an Y ."  ):
        return [  ( INSTANCE ,  mm["X"], mm["Y"] ) ]
    return None


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
