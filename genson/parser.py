# genson_parser.py
#
# Based on json parser code from Paul McGuire, 2007
#
#
genson_bnf = """
object 
    { members } 
    {} 
key
    string
    key_tuple
key_tuple
    ( key_list )
key_list
    string
    key_list, string
members 
    key : value 
    members , key : value
value_tuple
    ( elements )
    ()
array 
    [ elements ]
    [] 
elements 
    value 
    elements , value
generator
    kw ()
    kw (args)
    kw (kwargs)
    kw (args, kwargs)
args
    elements
kwargs
    kw = value
    kwargs , kw = value
value 
    string
    number
    object
    array
    true
    false
    value_tuple
    null
"""

from pyparsing import *
from functions import *
from references import ScopedReference
import functions
from collections import OrderedDict

# a simple helper functions
def make_genson_function(name, gen_args=[], gen_kwargs={}):

    generator_class = functions.registry.get(name, None)
    if generator_class is None:
        raise Exception('Unknown generator class: %s' % name)
    
    if type(gen_kwargs) is ParseResults:
        gen_kwargs = gen_kwargs.asList()
    gen_kwargs = dict(gen_kwargs)
    
    g = generator_class(*gen_args, **gen_kwargs)
    
    return g

def dummy_token(name):
    """  A allows for more sensible error reporting
    """
    exception_token = NoMatch()
    exception_token.setName("valid " + name)
    return exception_token


TRUE = Keyword("true").setParseAction( replaceWith(True) )
FALSE = Keyword("false").setParseAction( replaceWith(False) )
NULL = Keyword("null").setParseAction( replaceWith(None) )

json_string = dblQuotedString.setParseAction( removeQuotes )
json_number = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) +
                    Optional( '.' + Word(nums) ) +
                    Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )

genson_key_tuple = Forward()
genson_key = (dummy_token("key") | json_string | genson_key_tuple )
genson_key_tuple << Suppress('(') + delimitedList( genson_key ) + \
                         Suppress(')')
genson_key_tuple.setParseAction(lambda x: tuple(x))

genson_object = Forward()
genson_value = Forward()
json_elements = delimitedList( genson_value )
json_array = Group(Suppress('[') + Optional(json_elements) + Suppress(']') )

genson_value_tuple = Suppress('(') + json_elements + Suppress(')')
genson_value_tuple.setParseAction(lambda x: tuple(x))

THIS = Keyword("this")
PARENT = Keyword("parent")
ROOT = Keyword("root")
genson_initial_scope = (THIS | PARENT | ROOT)
genson_unquoted_key = Word(alphanums + '_')
genson_running_scope = ( PARENT | genson_unquoted_key )

genson_ref =  genson_initial_scope + \
                   Suppress('.') + \
                   delimitedList(genson_running_scope, '.')
                   
genson_ref.setParseAction(lambda x: ScopedReference(x.asList()))
                   

genson_kwargs = Group(delimitedList( Word(alphas) + Suppress("=") + \
                              genson_value ))
genson_function =  Word(alphas)("name") + \
                    Suppress('(') + \
                    Optional(json_elements)("args") + \
                    Optional(Suppress(',')) +\
                    Optional(genson_kwargs)("kwargs") + \
                    Suppress(')') 
genson_function.setParseAction(lambda x: make_genson_function(x.name, 
                                                              x.args, 
                                                              x.kwargs))

genson_grid_shorthand = Suppress("<") + \
                       json_elements("args") + \
                       Suppress(">") 
genson_grid_shorthand.setParseAction(lambda x: make_genson_function("grid", 
                                                                    x.args))

genson_value << (genson_value_tuple | genson_function | \
                genson_grid_shorthand | \
                genson_ref | \
                json_string | json_number | genson_object | \
                json_array | TRUE | FALSE | NULL )


genson_expression = (dummy_token("value") | operatorPrecedence( genson_value,
    [
     (Literal('^'), 2, opAssoc.RIGHT,   lambda x: x[0][0] ** x[0][2]),
     (Literal('-'), 1, opAssoc.RIGHT,    lambda x: -x[0][0]),
     (Literal('+'), 1, opAssoc.RIGHT,    lambda x: x[0][0]),
     (Literal('*'), 2, opAssoc.LEFT,     lambda x: x[0][0] * x[0][2]),
     (Literal('/'), 2, opAssoc.LEFT,     lambda x: x[0][0] / x[0][2]),
     (Literal('+'), 2, opAssoc.LEFT,     lambda x: x[0][0] + x[0][2]),
     (Literal('-'), 2, opAssoc.LEFT,     lambda x: x[0][0] - x[0][2]),
     ]
    ) )

member_def = Group( genson_key + Suppress(':') + genson_expression )
json_members = delimitedList( member_def )
empty_doc = Suppress('{') + Suppress('}')
genson_object << (Dict( Suppress('{') + json_members + Suppress('}') | empty_doc))

json_comment = cppStyleComment 
genson_object.ignore( json_comment )

def clean_dict(x):
    x_list = x.asList()
    return OrderedDict(x_list)

genson_object.setParseAction(clean_dict)

def convert_numbers(s,l,toks):
    n = toks[0]
    try:
        return int(n)
    except ValueError, ve:
        return float(n)
        
json_number.setParseAction( convert_numbers )
    
class GENSONParser:
    def __init__(self):
        self.grammar = genson_object
        self.grammar.enablePackrat()
    
    def parse_string(self, genson_string):
        result = self.grammar.parseString(genson_string)
        return result.asList()[0]

