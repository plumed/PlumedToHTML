from unittest import TestCase

import os
import json
from io import StringIO
from PlumedToHTML.PlumedCLFileLexer import PlumedCLFileLexer 
import PlumedToHTML
from pygments.formatters import HtmlFormatter

class TestPlumedLexer(TestCase):
   def testSimple(self) :
       # Open the json file and read it in
       f = open("tdata/clfiletests.json")
       tests = json.load(f)
       f.close()

       # Setup an HTML formatter
       f = HtmlFormatter()  

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item):
               tokensource = list(PlumedCLFileLexer().get_tokens(item["input"]))
               output = StringIO()
               f.format( tokensource, output )
               data = {}
               data["out"] = output.getvalue() 
               print( item["input"] )
               print( json.dumps( data, indent=3 ) )
               self.assertTrue( output.getvalue()==item["output"] )
               out = PlumedToHTML.get_cltoolfile_html( item["input"], "plinp" + str(item["index"]), ("plumed",) )
               self.assertTrue( PlumedToHTML.compare_to_reference( out, item ) )
