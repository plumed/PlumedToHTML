from unittest import TestCase

import os
import json
from io import StringIO
import subprocess
from bs4 import BeautifulSoup
from PlumedToHTML.PlumedLexer import PlumedLexer
from PlumedToHTML.PlumedFormatter import PlumedFormatter
from PlumedToHTML import compare_to_reference

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
       f = PlumedFormatter( keyword_file=keyfile, input_name="testout", hasload=False, broken=False, actions=set({}) )

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item): 
               print("INPUT", item["input"] )
               tokensource = list(PlumedLexer().get_tokens(item["input"]))
               output = StringIO() 
               f.format( tokensource, output )
               self.assertTrue( compare_to_reference( output.getvalue(), item ) )
               soup = BeautifulSoup( output.getvalue(), "html.parser" )
               for val in soup.find_all("b") :
                   if "onclick" in val.attrs.keys() : 
                      vallabel = val.attrs["onclick"].split("\"")[3]
                      self.assertTrue( soup.find("span", {"id": vallabel}) )
