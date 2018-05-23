"""
GRAMMAR

stmt_list -> stmt stmt_list
           |  ε
stmt -> var = expr
      | print expr
expr -> term term_tail
term_tail -> or term term_tail
          |  ε
term -> factor factor_tail
factor_tail -> and factor factor_tail
            | ε
factor -> not factor
        | ( expr )
        |  var
        |  boolean

var : όνομα μεταβλητής, ξεκινάει με γράμμα
boolean : boolean τιμή
print : Η λέξη ‘print’

----------------------------------------------

FIRST SETS

FIRST(stmt_list) = { var, print, ε }
FIRST(stmt) = { var, print }
FIRST(expr) = { not, ( , var , boolean }
FIRST(term_tail) = {or, ε}
FIRST(term) = { not, ( , var , boolean }
FIRST(factor_tail) = { and , ε}
FIRST(factor) = { not, ( , var , boolean }

---------------------------------------------

FOLLOW SETS

FOLLOW(stmt_list) = {$} 
FOLLOW(stmt) = {print, var, $}
FOLLOW(expr) = {print, var, ), $}

FOLLOW(term_tail) = {print, var, ), $}
FOLLOW(term) = {print, var, or, ), $}
FOLLOW(factor_tail) = {print, var, or, ), $}
FOLLOW(factor) = {print, var, or, and, ), $}

"""

import plex

class ParseError(Exception):
    pass

class MyParser:

    def create_scanner(self,fp):
        # Initializes scanner lexicon, patterns etc.
        self.command = ''
        boole = plex.Str('0','1','t','f','true','false','T','F','True','False','TRUE','FALSE') # boolean value
        variable = plex.Rep1(plex.Range("AZaz")) + plex.Rep(plex.Range("AZaz09")) # variable
        whitespace = plex.Any(" \t\n") # ignore these

        lexicon = plex.Lexicon([ #lexicon
            (whitespace,plex.IGNORE),
            (boole,'BOOLEAN'),
            (plex.Str('print'),'PRINT'),
            (plex.Str("or"),'OR'),
            (plex.Str("and"),'AND'),
            (plex.Str("not"),'NOT'),
            (plex.Str("("),'('),
            (plex.Str(")"),')'),
            (plex.Str('='),'='),
            (plex.Str(''),'None'),
            (variable,'VAR')
        ])

        self.scanner = plex.Scanner(lexicon,fp)
        self.la,self.val = self.next_token()


    def next_token(self):
        # Move onto the next token
        return self.scanner.read()

    def position(self):
        # Return scanner position, used for error logs
        return self.scanner.position()

    def match(self,token):
        # If token matches expected continue else raise error
        if self.la==token:
            self.la,self.val = self.next_token()
        else:
            raise ParseError("Found {} instead of {}".format(self.la,token))

    def parse(self,fp):
        # Starts the parser
        self.create_scanner(fp)
        self.stmt_list()
    
    def execute(self):
        # Execute function executes a python script that has same output
        # as the input
        exec(self.command)

    def stmt_list(self):
        # stmt_list -> stmt stmt_list
        #    |  ε
        self.command += '\n'
        if self.la =='PRINT':
            self.stmt()
            self.stmt_list()
        elif self.la == 'VAR':
            self.stmt()
            self.stmt_list()
        elif self.la == 'None':
            return
        else:
            raise ParseError("in stmt_list: expected print or var")

    def stmt(self):
        # stmt -> var = expr
        #   | print expr
        if self.la =='PRINT':
            self.command += 'print('
            self.match('PRINT')
            self.expr()
            self.command += ')'
        elif self.la == 'VAR':
            self.command += self.val
            self.match('VAR')
            self.command += ' ' + self.val
            self.match('=')
            self.expr()
        else:
            raise ParseError("in stmt: expected print or var")

    def expr(self):
        # expr -> term term_tail
        if self.la =='VAR' or self.la == 'NOT' or self.la == '(' or self.la == 'BOOLEAN':
            self.term()
            self.term_tail()
        else:
            raise ParseError("in expr: expected var, not, boolean, ( ")

    def term_tail(self):
        # term_tail -> or term term_tail
        #   |  ε
        if self.la =='OR':
            self.command += ' ' + self.val
            self.match('OR')
            self.term()
            self.term_tail()
        elif self.la =='VAR' or self.la == 'PRINT' or self.la == ')':
            return
        elif self.la == 'None':
            return
        else:
            raise ParseError("in term_tail: expected print, variable, or, ) ")


    def term(self):
        # term -> factor factor_tail
        if self.la =='VAR' or self.la == 'NOT' or self.la == '(' or self.la == 'BOOLEAN':
            self.factor()
            self.factor_tail()
        else:
            raise ParseError("in term: expected var, not, (, boolean")

    def factor_tail(self):
        # factor_tail -> and factor factor_tail
        # | ε
        if self.la =='AND':
            self.match('AND')
            self.command += ' and '
            self.factor()
            self.factor_tail()
        elif self.la == 'PRINT' or self.la == 'VAR' or self.la == 'OR' or self.la == ')':
            return
        elif self.la == 'None':
            return
        else:
            raise ParseError("in factor_tail: expected print, var , or , ) ")


    def factor(self):
        # factor -> not factor
        # | ( expr )
        # |  var
        # |  boolean
        if self.la =='BOOLEAN':
            if self.val == '1' or self.val == 't' or self.val == 'T' or self.val == 'true' or self.val == 'TRUE' or self.val == 'True':
                self.command += ' ' + "True"
            else:
                self.command += ' ' + "False"
            self.match('BOOLEAN')
        elif self.la == '(':
            self.command += ' ' + self.val
            self.match('(')
            self.expr()
            self.command += ' ' + self.val
            self.match(')')
        elif self.la == 'VAR':
            self.command += ' ' + self.val
            self.match('VAR')
        elif self.la == 'NOT':
            self.command += ' ' + self.val
            self.match('NOT')
            self.factor()
        else:
            raise ParseError("in factor: expected boolean, ( ,var, not  ")

# create the parser object
parser = MyParser()

# open file for parsing
with open("input.txt","r") as fp:

    # parse file
    try:
        parser.parse(fp)
        print("Valid input!")
    except plex.errors.PlexError:
        _,lineno,charno = parser.position()	
        print("Scanner Error: at line {} char {}".format(lineno,charno+1))
    except ParseError as perr:
        _,lineno,charno = parser.position()	
        print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))