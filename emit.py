import os
from typing import List, Tuple, Union , Dict, Any , Generator
from parser import ASTNode,  SourceLocation, LiteralNode, IdentifierNode

def isSameIdentifierNode(  a , b  ) -> bool:
        #compare lists of IdentifierNode by value
        # red book == Red Book
        # unamed-name == unamed -name  , ie remove spaces for compare 
        
        # a is a list of identifierNode?
        if  isinstance(a, list) and isinstance(a[0], IdentifierNode)  :
            a_str = ''.join( [ n.value.lower() for n in a if n.value.strip() != '' ] )
        if isinstance(b, list) and isinstance(b[0], IdentifierNode)  :
            b_str = ''.join( [ n.value.lower() for n in b if n.value.strip() != '' ] ) 
        
        # a is an identifierNode?
        if isinstance(a, IdentifierNode) :
            a_str = a.value.lower().replace(" ","")
        if isinstance(b, IdentifierNode) :    
            b_str = b.value.lower().replace(" ","")
            
        #a or b is string ?
        if isinstance(a, str):
            a_str = a.lower().replace(" ","")
        if isinstance(b, str):    
            b_str = b.lower().replace(" ","")
                
        return a_str == b_str

def _IdentifierNodeToString(  a , articles ) -> Tuple[str, str]:
        #convert list of IdentifierNode to string
        if  isinstance(a, list) :
            if isinstance(a[0], IdentifierNode)  :
                #is an article?
                first_word = a[0].value.lower().strip()
                if first_word in articles and len(a) > 1:
                    art =  first_word 
                    _, name = _IdentifierNodeToString( a[1:] , articles )
                    return art, name
                else:
                     
                    name = ' '.join( [ n.value for n in a ] )
                    return "" , name
        if isinstance(a, IdentifierNode) :
            #is an article ?    
            return _IdentifierNodeToString( a.value , articles )
        if isinstance(a, str):
            #is an article ?
            first_word = a.lower().strip().split(" ")[0]
            if first_word in articles:
                art = first_word
                rest = a[len(first_word):].strip()
                return art , rest
            else:
                return "" , a
        return "" , ""

def IdentifierNodeToString(  a , articles ) -> Tuple[str, str]:
    art,ident =  _IdentifierNodeToString( a , articles )
    print(f" {a} IdentifierNodeToString-> {art, ident} ")
    return art, ident

INSTANCE = "CreateInstance"
CVAR_ENUM = "CreateCVarEnum"
CVAR_KIND = "CreateCVarKind"
INITIAL_ASSIGN   = "CreateInitialAssert"
SUBCLASS = "CreateSubClass"

class Kind:
    def __init__(self, name: str , kind):
        self.name = name
        self.kind = kind
        #this variables are copyed to instances of this kind
        self.enumVariables = {}  # internalVariableName -> values Example:  _var00654: [open, closed]
        self.kindVariables = {}

 

class VariableEnum:
    def __init__(self, id: str,  options: List[str] ):
        self.id = id # _var00001...
        self.options = options
        self.initial_value = None
    def copy(self):
        v = VariableEnum( self.id , self.options.copy() )
        v.initial_value = self.initial_value
        return v    

class VariableKind:
    def __init__(self, id: str, name:str,   kind: Kind ):
        self.id = id  # _var00002...
        self.name = name # description, color ...
        self.kind = kind
        self.initial_value = None 
        
    def copy(self):
        v = VariableKind( self.id , self.name , self.kind )
        v.initial_value = self.initial_value
        return v    
 

class Instance:
    def __init__(self, name: str, kind: Kind):
        self.name = name
        self.kind = kind
        self.enumVariables = {}  # internalVariableName -> values Example:  _var00654: [open, closed]
        self.kindVariables = {}
        
        
 
class  ErrorCompile:
    def __init__(self, msg: str):
        self.msg = msg
    def __str__(self):
        return f"Compile Error: {self.msg}"
 
class Program:
    def __init__(self):
        self.kinds = []
        self.instances = [] 
        self.variable_index = 0 
        
        self.articles = [ "a" , "an" , "the" ] 
        
        #add primitive types : Integer, Text, Boolean
        self.kinds.append( Kind( "Integer" , None ) )
        self.kinds.append( Kind( "Text" , None ) )
        self.kinds.append( Kind( "Boolean" , None ) )
        
    def createInstance( self , instanceName: str , kind: Kind ):
        i = Instance( instanceName , kind )
        #copy variables from upper kinds
        superKinds = self.getAllSuperKinds( kind )
        print(f"Creating instance {instanceName} of kind {kind.name} with superkinds {[ sk.name for sk in superKinds ] } ")
        for sk in  superKinds:
            for var_id, var in sk.enumVariables.items():
                #skip if already exist
                if var_id not in i.enumVariables:
                    i.enumVariables[ var_id ] = var.copy()
            for var_id, var in sk.kindVariables.items():
                if var_id not in i.kindVariables:
                    print(f" Copying kind variable {var_id} to instance {instanceName} , called {var.name} of kind {var.kind.name} ")
                    i.kindVariables[ var_id ] = var.copy()
        self.instances.append( i )
        return i 
    
    def createKind( self , kindName: str , superKind: Union[Kind, None] ):
        k = Kind( kindName , superKind )
        superKinds = self.getAllSuperKinds( k )
        for sk in  superKinds:
            for var_id, var in sk.enumVariables.items():
                #skip if already exist
                if var_id not in k.enumVariables:
                    k.enumVariables[ var_id ] = var.copy()
            for var_id, var in sk.kindVariables.items():
                if var_id not in k.kindVariables:
                    print(f" Copying kind variable {var_id} to kind {kindName} , called {var.name} of kind {var.kind.name} ")
                    k.kindVariables[ var_id ] = var.copy()
                    
        self.kinds.append( k )
        return k

    def isSubClassOf( self , sub: Union[Kind, Instance] , superK: Kind ) -> bool:        
        if sub.name == superK.name:
            return True
        if sub.kind is None:
            return False
        return self.isSubClassOf( sub.kind , superK )

    def getNewVariableId(self) -> str:
        name = f"_var{self.variable_index:05d}"
        self.variable_index += 1
        return name
    
    def addEnumVariable( self , target: Union[Kind, Instance] , variableId: str , options: List[str] ):
        print(f"Adding enum variable {variableId} with options {options} to target '{target.name}' ")
        target .enumVariables[ variableId ] = VariableEnum( variableId , options )
        #find all instances of this kind and add the variable too
        for instance in self.instances + self.kinds:
            if self.isSubClassOf( instance , target ):
                if variableId not in instance.enumVariables:
                    instance.enumVariables[ variableId ] = VariableEnum( variableId , options )

    def addKindVariable( self , target: Union[Kind, Instance] , variableId: str , varName: str , varKind: Kind ):
        print(f"Adding kind variable {variableId} named '{varName}' of kind '{varKind.name}' to target '{target.name}' ")
        target.kindVariables[ variableId ] = VariableKind(  variableId , varName , varKind )
        #find all instances of this kind and add the variable too
        for instance in self.instances + self.kinds:
            if self.isSubClassOf( instance , target ):
                if variableId not in instance.kindVariables:
                   instance.kindVariables[ variableId ] = VariableKind(  variableId , varName , varKind )

    def findVarIdbyPossibleValue( self , target: Union[Kind, Instance] , possible_value: Any ) -> Union[str, None]:
        #possible_value can be list of IdentifierNode or single IdentifierNode or string
        for var_id, var in target.enumVariables.items():
            for option in var.options:
                #print(f"Comparing option {option} to possible_value {possible_value} ")
                if isSameIdentifierNode( option , possible_value ):
                    return var_id 
        return None
    
        
    def getKindByName(self, name: Any) -> Union[Kind, None]:
        #bame can be list of IdentifierNode or single IdentifierNode or string
        for k in self.kinds:
            if isSameIdentifierNode( k.name , name ):
                return k
        return None

    def getInstanceByName(self, name: Any) -> Union[Instance, None]:
        for inst in self.instances:            
            if isSameIdentifierNode( inst.name , name ):
                return inst
        return None

    def getAllSuperKinds(self, kind: Kind) -> List[Kind]:
        supers = []
        current = kind
        while current is not None:
            supers.append( current )
            current = current.kind
        return supers
    
    def getPropertyByName(self, propertyCompose: Any) -> Union[VariableKind, None]:
        #search by combination of :
        # property of instance : description of book, color of ball
        # property of kind : description of thing , color of object
        # adjective of instance : book description , ball color
        # adjective of kind : thing description , object color
        print(f"Searching property {propertyCompose} ")
        for entity in self.instances + self.kinds:
            print(f" Checking entity {entity.name} ")
            for prop_id in entity.kindVariables:
                aName = entity.name + " " + entity.kindVariables[prop_id].name
                print(f" Comparing {aName} to {propertyCompose} ")
                if isSameIdentifierNode( aName , propertyCompose ):
                    print(f" Found property {entity.kindVariables[prop_id].name} of entity {entity.name} by adjective form ")
                    return entity,  prop_id
                pName = entity.kindVariables[prop_id].name + " of " + entity.name
                print(f" Comparing {pName} to {propertyCompose} ")
                if isSameIdentifierNode( pName , propertyCompose ):
                    print(f" Found property {entity.kindVariables[prop_id].name} of entity {entity.name} by property form ")
                    return entity.kindVariables[prop_id]

        return None,None
        
    def initVars(self):
        #initialize variables with initial values
        for instance in self.instances:
            for sk in self.getAllSuperKinds( instance.kind ):
                for var_id, var in sk.enumVariables.items():
                    if var.initial_value is not None:
                        instance.enumVariables[ var_id ].initial_value = var.initial_value
                for var_id, var in sk.kindVariables.items():
                    if var.initial_value is not None:
                        instance.kindVariables[ var_id ].initial_value = var.initial_value
            

    def emit(self, instruction: tuple):
        #is not tuple ? raise error
        if not isinstance(instruction, tuple):
            return ErrorCompile(f"Invalid instruction format: {instruction}")
        
        if instruction[0] == INSTANCE:
            _, X, Y = instruction
            article , instanceName = IdentifierNodeToString( X , self.articles )
            _, iKindName = IdentifierNodeToString( Y , self.articles )
           
            print(f"Emitting: CreateInstance of {iKindName} named {instanceName}")
            iKind = self.getKindByName( iKindName )
            if iKind is None:
                return ErrorCompile(f"Kind {iKindName} not defined for instance {instanceName}")
            self.createInstance( instanceName , iKind )
            return None
           
        
        if instruction[0] == SUBCLASS:
            _, X, Y = instruction
            _, subClassName = IdentifierNodeToString( X ,self.articles )
            
            if Y is None:
                superKind = None
            else:    
                _, superKindName = IdentifierNodeToString( Y ,self.articles )
                superKind = self.getKindByName( superKindName )            
                if superKind is None:
                    return ErrorCompile(f"SuperKind {superKindName} not defined for kind {subClassName}")
           
            self.createKind( subClassName , superKind )
            return None
        
        if instruction[0] == CVAR_ENUM:
            _, X, options = instruction
            article , identifier = IdentifierNodeToString( X ,self.articles )
            print(f"Emitting: CreateCVarEnum for {identifier} with options {[ [n.value for n in opt ] for opt in options ] }")
            target = self.getInstanceByName( identifier )
            if target is None:
                target = self.getKindByName( identifier )                

            if target is None:             
                return ErrorCompile(f"Instance {identifier} not defined ") 
            variableId = self.getNewVariableId()
            values = [IdentifierNodeToString(opt, self.articles)[1] for opt in options]
            self.addEnumVariable( target , variableId , values )
            return None
        
        
        if instruction[0] == INITIAL_ASSIGN:
            print(f"Processing INITIAL_ASSIGN: {instruction} ")
            _, X, Y = instruction
            if isinstance(Y, list):
                if len(Y) == 1:
                    Y = Y[0]
            article , identifier = IdentifierNodeToString( X ,self.articles )  
            print(f" XX { article} , {identifier} " )   
            target = self.getInstanceByName( identifier )
            if target is None:
                target = self.getKindByName( identifier )
            if isinstance(Y, IdentifierNode) or isinstance(Y, list):
                targetValue = IdentifierNodeToString( Y , self.articles )[1]
            elif isinstance(Y, LiteralNode):
                #an Text 
                targetValue = Y           
          
            if not (target is None):
                #the assign is for an Enum variable of an instance/kind.
                # book is small -> assign initial value 'small' to variable of instance 'book', on enum variable thats contains something like small, big , medium    
                 
                var = self.findVarIdbyPossibleValue( target, targetValue )
                if var is None:
                    return ErrorCompile(f"Variable for value {Y} not found in instance/kind {identifier} for initial assignment ")
                print(f" Found variable id {var} for initial assignment "   )
                var = target.enumVariables[ var ]
                var.initial_value = targetValue
                print(f"Assigned initial value {targetValue} to variable {var.id} of instance/kind {identifier} ")
            else:
                #the assign is for a property of an instance/kind
                # the book description is "an old and misterious book"  -> assign initial value
                target, prop_id = self.getPropertyByName( identifier )
                if prop_id is None:
                    return ErrorCompile(f"Property {identifier} not found for initial assignment ")

                target.kindVariables[ prop_id ].initial_value = targetValue
                print(f"Assigned initial value {targetValue} to property {target.kindVariables[prop_id].name} of instance/kind {target.name} ")

              
            return None
        
        if instruction[0] == CVAR_KIND:
            _, X, Y, Z = instruction
            article , identifier = IdentifierNodeToString( X ,self.articles )
            target =  self.getInstanceByName( identifier )
            if target is None:
                target = self.getKindByName( identifier )
            if target is None:             
                return ErrorCompile(f"target {identifier} not defined for CVAR_KIND ") 
            _, varKindName = IdentifierNodeToString( Y ,self.articles )
            varKind = self.getKindByName( varKindName )
            if varKind is None:
                return ErrorCompile(f"Kind {varKindName} not defined for CVAR_KIND ")
            _, varName = IdentifierNodeToString( Z ,self.articles )
            variableId = self.getNewVariableId()            
            self.addKindVariable( target , variableId , varName , varKind )
            return None
                
        return ErrorCompile(f"Unknown instruction type: {instruction[0]}") 