from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Keyword, Name, String

class PlumedCLtoolLexer(RegexLexer):
    name = 'plumedcltool'
    aliases = ['plumedcltool']
    filenames = ['*.plmd']

    tokens = {
        'root': [
            # Find commands that take an input file
            (r'(^\s*plumed)(\s+)(\S*\b)(\s*<\s*)(\S+\b)', bygroups(String, Text, Keyword, Text, Name.Decorator)),
            # Find the name of the command
            (r'(^\s*plumed)(\s+)(\S*\b)', bygroups(String, Text, Keyword)),
            # Deals with keywords with equals sign
            (r'(-\S+)(=)(\S+\b)', bygroups(Name.Attribute, Text, Text)),
            # Deals with keywords
            (r'(-\S+)(\s+)(\S+\b)', bygroups(Name.Attribute, Text, Text)),
            # Deals with flags
            (r'(-\S+\b)', Name.Attribute),
            # Find any left over white space
            (r'\s+',Text)
        ]
    }
