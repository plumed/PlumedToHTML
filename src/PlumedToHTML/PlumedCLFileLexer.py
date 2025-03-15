from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Keyword, Name, String, Comment

class PlumedCLFileLexer(RegexLexer):
    name = 'plumedclfile'
    aliases = ['plumedclfile']
    filenames = ['*.plmd']

    tokens = {
        'root': [
            # Find the start of a shortcut with a nested default
            (r'#NODEFAULT plumed\n',Comment.Special),
            # Find the start of a default section
            (r'#DEFAULT plumed\n',Comment.Special),
            # Find the end of a default section
            (r'#ENDDEFAULT plumed\n',Comment.Special),
            # The name of the tool that this is an input file for
            (r'(#TOOL=\s*)(\S+\b)',bygroups( Comment, Keyword )),
            # The lines of instruction for the file  
            (r'(\S+\b)(\s+)(.+$)',bygroups(Name.Attribute, Text, Text)),
            # Find any left over white space
            (r'\s+',Text)
        ]
    }
