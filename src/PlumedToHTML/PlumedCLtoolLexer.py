from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Keyword, Name, String, Comment

class PlumedCLtoolLexer(RegexLexer):
    name = 'plumedcltool'
    aliases = ['plumedcltool']
    filenames = ['*.plmd']

    tokens = {
        'root': [
            # Find the start of a shortcut with a nested default
            (r'#NODEFAULT plumed\n',Comment.Special),
            # Find the start of a default section
            (r'#DEFAULT plumed\n',Comment.Special),
            # Find the end of a default section
            (r'#ENDDEFAULT plumed\n',Comment.Special),
            # Find commands that take an input file
            (r'(^\s*plumed)(\s+)(\S+\b)(\s*<\s*)(\S+\b)', bygroups(String, Text, Keyword, Text, Name.Decorator)),
            # Find the name of the command
            (r'(^\s*plumed)(\s+)(\S+\b)', bygroups(String, Text, Keyword)),
            # Deals with keywords with equals sign
            (r'(-\S+)(=)(\S+\b)', bygroups(Name.Attribute, Text, Text)),
            # Flag at end of line
            (r'(--\S+\b)(\s*\n)', bygroups(Name.Attribute, Text)),
            # Deals with keywords
            (r'(--\S+)(\s+)([^-\s]+\b)', bygroups(Name.Attribute, Text, Text)),
            # Deals with flags
            (r'(--\S+\b)', Name.Attribute),
            # find the -h command
            (r'(-h)', Name.Attribute),
            # Find any left over white space
            (r'\s+',Text)
        ]
    }
