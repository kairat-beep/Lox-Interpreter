import sys
import os
from enum import Enum,auto

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class TokenType(Enum):
    #Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    #One or two character tokens.
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    #Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    #Keywords.
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    EOF = auto()

class Token():

    #Token of a text
    def __init__(self,token:TokenType,lexeme:str = None, line:int = None,literal:str = None):
        self.token = token
        self.lexeme = lexeme 
        self.line = 0 
        self.literal = literal

    def __repr__(self):
        if self.literal is None:
            self.literal = 'null'
        return (f'{self.token.name} {self.lexeme} {self.literal}')

class Scanner():

    KEYWORDS = [(i.name.lower(), i) for i in [TokenType.AND, TokenType.CLASS, TokenType.ELSE, TokenType.FALSE, TokenType.FUN, TokenType.FOR, TokenType.IF, TokenType.NIL, TokenType.OR, TokenType.PRINT, TokenType.RETURN, TokenType.SUPER, TokenType.THIS, TokenType.TRUE, TokenType.VAR, TokenType.WHILE, TokenType.EOF]]
    def __init__(self, text:str):
        self.code = text
        self.reset() 

    def reset(self):
        self.tokens = []
        self.index = 0 
        self.line = 1
        self.error = False

    def addToken(self, token: TokenType, lexeme : str = None, literal: str = None):
        if lexeme == None:
            lexeme = self.getLexeme()
        self.tokens.append(Token(token, lexeme, self.line, literal))

    def getLexeme(self):
        return self.code[self.index-1]

    def nextLine(self):
        self.line += 1

    def scanToken(self):
        char = self.code[self.index]
        self.index = self.index + 1
        return char 

    def isEOF(self):
        return self.index>=len(self.code)
    
    def isEOL(self):
        return self.peek(os.linesep)

    def match(self,chr):
        if self.isEOF():
            return False

        if self.code[self.index] == chr:
            self.index += 1
            return True
        return False 

    def scanSpace(self):
        chars = []
        while(not self.isEOF() and (not self.isEOL() and not self.peek() == ' ')):
            chars.append(self.scanToken())
        return ''.join(chars) 

    def peek(self, chr = None):
        if self.isEOF():
            return False
        if chr is None:
            return self.code[self.index]
        if self.code[self.index] == chr:
            return True
        return False

    def peekNext(self):
        if self.index+1<len(self.code):
            return self.code[self.index+1]
        else:
            None

    def scan(self):
        while self.index < len(self.code):
            type = None
            newString = []
            match self.scanToken():
                case '(': 
                    self.addToken(TokenType.LEFT_PAREN)
                case ')': 
                    self.addToken(TokenType.RIGHT_PAREN)
                case '{': 
                    self.addToken(TokenType.LEFT_BRACE)
                case '}': 
                    self.addToken(TokenType.RIGHT_BRACE)
                case ',': 
                    self.addToken(TokenType.COMMA)
                case '.': 
                    self.addToken(TokenType.DOT)
                case '-': 
                    self.addToken(TokenType.MINUS)
                case '+': 
                    self.addToken(TokenType.PLUS)
                case ';': 
                    self.addToken(TokenType.SEMICOLON)
                case '*': 
                    self.addToken(TokenType.STAR)
                case '/': 
                    if self.match('/'):
                        while(not self.isEOF() and not self.isEOL()):
                            self.scanToken()
                    else:
                        self.addToken(TokenType.SLASH)
                case '!':
                    tokenString='!'
                    if self.match("="):
                        type = TokenType.BANG_EQUAL  
                        tokenString = '!='
                    else:
                        type = TokenType.BANG
                    self.addToken(type, tokenString) 
                case '=':
                    tokenString='='
                    if self.match("="):
                        type = TokenType.EQUAL_EQUAL
                        tokenString = '=='
                    else:
                        type = TokenType.EQUAL
                    self.addToken(type, tokenString) 
                case '<':
                    tokenString='<'
                    if self.match("="):
                        type = TokenType.LESS_EQUAL
                        tokenString = '<='
                    else:
                        type = TokenType.LESS
                    self.addToken(type, tokenString) 
                case '>':
                    tokenString='>'
                    if self.match("="):
                        type = TokenType.GREATER_EQUAL  
                        tokenString = '>='
                    else:
                        type = TokenType.GREATER
                    self.addToken(type, tokenString) 
                case os.linesep:
                    self.nextLine()
                case ' '|'\t':
                    pass
                case '"':
                    while(not self.isEOF()  and not self.peek('"')):
                            newString.append(self.scanToken())
                    if self.isEOF() or not self.isEOF() and not self.peek('"'):
                        eprint(f"[line {self.line}] Error: Unterminated string.")
                        self.error = True
                    else:
                        not self.isEOF() and self.scanToken()
                        self.addToken(TokenType.STRING,f'"{''.join(newString)}"',''.join(newString))
                case _ as char:
                    newString.append(char)
                    if char.isdigit():
                        numDots = 0
                        while(not self.isEOF() and not self.isEOL() and self.peek().isdigit()):
                            newString.append(self.scanToken())
                            #Consume floats    " ###.###"
                            if numDots<1 and not self.isEOF() and self.peek('.') and self.peekNext() is not None and self.peekNext().isdigit():
                                numDots += 1
                                newString.append(self.scanToken())
                        number=numberL = ''.join(newString)
                        if numDots >0:
                            while newString[-1]=='0':
                                newString.pop() 
                            numberL = ''.join(newString)
                        self.addToken(TokenType.NUMBER,number ,float(numberL))
                    elif char.isalpha() or char =='_':
                       while(not self.isEOF() and not self.isEOL() and (self.peek() == '_' or self.peek().isalnum())):
                            newString.append(self.scanToken())
                       word = ''.join(newString)
                       tType = TokenType.IDENTIFIER
                       for keyword,tokenType in Scanner.KEYWORDS:
                            if keyword == word:
                                tType = tokenType
                                break
                       self.addToken(tType, word)
                    elif char == '.':
                        self.addToken(TokenType.DOT)
                    else:
                        eprint(f'[line {self.line}] Error: Unexpected character: {char}')#Ignore 
                        self.error = True
        return len(self.tokens) > 0


    def __repr__ (self):
        return f'{os.linesep}'.join([str(i) for i in self.tokens])

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file = sys.stderr)

    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file = sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command !=  "tokenize":
        print(f"Unknown command: {command}", file = sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)

    if scanner.scan():
        print(str(scanner))
    print("EOF  null") # Placeholder, remove this line when implementing the scanner
    if scanner.error:
        sys.exit(65)

if __name__ ==  "__main__":
    main()
