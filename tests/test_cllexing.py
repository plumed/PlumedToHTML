from unittest import TestCase

import os
import json
from io import StringIO
from pygments.formatters import HtmlFormatter

import PlumedToHTML

class TestPlumedLexer(TestCase):
   def lexerTestTemplate(self,file:str, lexerFunc, htmlFunction) :
       # Open the json file and read it in
      with open(file) as f:
         tests = json.load(f)

      # Setup an HTML formatter
      formatter = HtmlFormatter()  

      # Now run over all the inputs in the json
      for item in tests["regtests"] :
         with self.subTest(item=item,msg=item["input"]):
            tokensource = list(lexerFunc().get_tokens(item["input"]))
            output = StringIO()
            formatter.format( tokensource, output )
            data = {}
            data["out"] = output.getvalue() 
            print( f'**INPUT:"{item["input"]}"' )
            print( json.dumps( data, indent=3 ) )
            self.assertEqual( output.getvalue(),item["output"] )
            out = htmlFunction( item["input"], "plinp" + str(item["index"]), ("plumed",) )
            self.assertTrue( PlumedToHTML.compare_to_reference( out, item ) )

   def testCLtoolLexer(self) :
      from PlumedToHTML.PlumedCLtoolLexer import PlumedCLtoolLexer 
      self.lexerTestTemplate("tdata/cltooltests.json",PlumedCLtoolLexer, PlumedToHTML.get_cltoolarg_html)
   
   def testCLFileLexer(self) :
      from PlumedToHTML.PlumedCLFileLexer import PlumedCLFileLexer 
      self.lexerTestTemplate("tdata/clfiletests.json",PlumedCLFileLexer, PlumedToHTML.get_cltoolfile_html)
