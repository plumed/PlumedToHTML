from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Comment, Literal, Keyword, Name, Generic, String

class PlumedLexer(RegexLexer):
    name = 'plumed'
    aliases = ['plumed']
    filenames = ['*.plmd']

    tokens = {
        'defaults' : [
            # Deals with blank lines
            (r'\s+$', Text),
            # Deals with all comments
            (r'#.*?$', Comment),
            # Deals with incomplete inputs 
            (r'__FILL__', Literal),  
            # Find LABEL=lab
            (r'(LABEL)(=)(\S+\s)', bygroups(Name.Attribute, Text, String)),
            # Find special replica syntax with brackets
            (r'(\w+)(=)(@replicas:)((?s)\{.*?\})', bygroups(Name.Attribute, Text, Name.Constant, Generic)),  
            # Find special replica syntax without brackets
            (r'(\w+)(=)(@replicas:)(\S+\s)', bygroups(Name.Attribute, Text, Name.Constant, Generic)),
            # Find KEYWORD with brackets around value
            (r'(\w+)(=)((?s)\{.*?\})', bygroups(Name.Attribute, Text, Generic)),
            # Find KEYWORD=whatever 
            (r'(\w+)(=)(\S+\s)', bygroups(Name.Attribute, Text, Generic))
         ],
        'root': [
            # Find the start of shortcuts
            (r'#SHORTCUT.*?\r?\n',Comment.Special),
            # Find the start of a shortcut with a nested default
            (r'#NODEFAULT.*?\r?\n',Comment.Special),
            # Find the start of a default section
            (r'#DEFAULT.*?\r?\n',Comment.Special),
            # Find the end of a default section
            (r'#ENDDEFAULT.*?\r?\n',Comment.Special),
            # Find the middle of shortcuts
            (r'#EXPANSION.*?\r?\n',Comment.Special),
            # Find the end of shortcuts
            (r'#ENDEXPANSION.*?\r?\n',Comment.Special),
            include('defaults'), 
            # Find label: ACTION
            (r'(\w+)(:\s+)(\S+\s)', bygroups(String, Text, Keyword)),
            # Find ... for start of continuation
            (r'\.\.\.', Text, 'continuation'),
            # Find ACTION at start of line
            (r'^\s*\w+\s',Keyword),
            # Find FLAG anywhere on line
            (r'\w+\b',Name.Attribute),
            # Find any left over white space
            (r'\s+',Text)
        ],
        'continuation' : [
            include('defaults'),
            # Find FLAG which can now be anywhere on line or at start of line in continuation
            (r'\w+\s', Name.Attribute),
            # Find any left over white space 
            (r'\s+', Text),
            # Find ... ACTION as end of continuation
            (r'(\.\.\.\s+)(\S+$)', bygroups(Text, Text), '#pop'),
            # Find ... as end of continuation
            (r'\.\.\.', Text, '#pop')
        ]
    }
