from unittest import TestCase

import os
import json
from io import StringIO
import subprocess
from PlumedToHTML.PlumedLexer import PlumedLexer
from PlumedToHTML.PlumedFormatter import PlumedFormatter

class TestPlumedFormatter(TestCase):
   def testSimple(self) :
       # Open the json file and read it in
       f = open("tdata/formattests.json")
       tests = json.load(f)
       f.close()

       # Get the plumed syntax file
       cmd = ['plumed', 'info', '--root']
       plumed_info = subprocess.run(cmd, capture_output=True, text=True )
       keyfile = plumed_info.stdout.strip() + "/json/syntax.json"

       # Setup a plumed formatter
       f = PlumedFormatter( keyword_file=keyfile, input_name="testout" )

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item): 
               tokensource = list(PlumedLexer().get_tokens(item["input"]))
               output = StringIO() 
               f.format( tokensource, output )
               self.assertTrue( output.getvalue()==item["output"] )
