from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Comment, Literal, Keyword, Name, Generic, String

class PlumedLexer(RegexLexer):
    name = 'plumed'
    aliases = ['plumed']
    filenames = ['*.plmd']

    tokens = {
        'defaults' : [
            # Deals with blank space
            (r'\s+$', Text),
            # Deals with all comments
            (r'#.*?$', Comment),
            # Deals with incomplete inputs 
            (r'(__FILL__)(=)(\S+\b)', bygroups(Literal, Text, Generic)),
            (r'(\w+)(=)(__FILL__)', bygroups(Name.Attribute, Text, Literal)),
            (r'__FILL__', Literal),  
            # Find LABEL=lab
            (r'((?i)LABEL)(=)(\S+\b)', bygroups(Name.Attribute, Text, String.Double)),
            # Find special replica syntax with fill
            (r'(\w+)(=)(@\S+:)(__FILL__)', bygroups(Name.Attribute, Text, Name.Constant, Literal)), 
            # Find special replica syntax with brackets around replica command
            (r'(\w+)(=\{)(@\S+:)((?s)\{.*?\})(\})', bygroups(Name.Attribute, Text, Name.Constant, Generic, Text)),
            # Find special replica syntax with brackets
            (r'(\w+)(=)(@\S+:)((?s)\{.*?\})', bygroups(Name.Attribute, Text, Name.Constant, Generic)),  
            # Find special replica syntax without brackets
            (r'(\w+)(=)(@\S+:)(\S+\b)', bygroups(Name.Attribute, Text, Name.Constant, Generic)),
            # Find KEYWORD with brackets around value
            (r'(\w+)(=)((?s)\{.*?\})', bygroups(Name.Attribute, Text, Generic)),
            # Find KEYWORD=whatever 
            (r'(\w+)(=)(\S+\b)', bygroups(Name.Attribute, Text, Generic))
         ],
        'root': [
            # Deals with blank lines
            (r'^\n', Text.Whitespace),
            # Find comment reversion stuff
            (r'(^# The command:\n)(#.+\n)(# ensures PLUMED loads the contents of the file called .+$)',bygroups(Comment, Comment.Hashbang, Comment)),
            # And stuff for long versions of shortcuts
            (r'(^# PLUMED interprets the command:\n)(#.+$)', bygroups(Comment, Comment.Hashbang)),
            # Find ENDPLUMED and set everything after it to a comment
            (r'(^\s*ENDPLUMED)((?s).*\Z)', bygroups(Keyword, Comment)),
            # Find the start of shortcuts
            (r'#SHORTCUT.*?\r?\n',Comment.Preproc),
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
            # Find vimsyntax expression
            (r'#\s*vim:\s*ft=plumed',Literal),
            # Include all the default stuff
            include('defaults'), 
            # Find label: __FILL__
            (r'(.+)(:\s+)(__FILL__)', bygroups(String, Text, Literal)),
            # Find label: ACTION
            (r'(.+)(:\s+)(\S+\b)', bygroups(String, Text, Keyword)),
            # Find label: ... \n ACTION  
            (r'(.+)(:\s+\.\.\.\s*$\s*)(\S+\b)', bygroups(String, Text, Keyword), 'continuation'),
            # Find ... for start of continuation
            (r'\.\.\.', Text, 'continuation'),
            # Find ACTION at start of line
            (r'^\s*\w+\b',Keyword),
            # Find FLAG anywhere on line
            (r'\w+\b',Name.Attribute),
            # Find any left over white space
            (r'\s+',Text)
        ],
        'continuation' : [
            include('defaults'),
            # Find FLAG which can now be anywhere on line or at start of line in continuation
            (r'\w+\b', Name.Attribute),
            # Find any left over white space 
            (r'\s+', Text),
            # Find ... ACTION as end of continuation
            (r'(\.\.\.)(.+$)', bygroups(Text, Text), '#pop'),
            # Find ... as end of continuation
            (r'\.\.\.', Text, '#pop')
        ]
    }
