from unittest import TestCase

import os
import json
from io import StringIO
import subprocess
from bs4 import BeautifulSoup
from PlumedToHTML.PlumedLexer import PlumedLexer
from PlumedToHTML.PlumedFormatter import PlumedFormatter
from PlumedToHTML import compare_to_reference
from PlumedToHTML import getPlumedSyntax

class TestPlumedFormatter(TestCase):
   def testSimple(self) :
       # Open the json file and read it in
       f = open("tdata/formattests.json")
       tests = json.load(f)
       f.close()

       # Get the plumed syntax file
       keydict = getPlumedSyntax( ("plumed",) )

       # Setup a plumed formatter
       f = PlumedFormatter( keyword_dict=keydict, input_name="testout", hasload=False, broken=False, actions=set({}), valuedict=dict({}), auxinputs=[], auxinputlines=[] )

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item): 
               print("INPUT", item["input"] )
               tokensource = list(PlumedLexer().get_tokens(item["input"]))
               output = StringIO() 
               f.format( tokensource, output )
               # Check for clickable labels
               self.assertTrue( compare_to_reference( output.getvalue(), item ) )
               soup = BeautifulSoup( output.getvalue(), "html.parser" )
               for val in soup.find_all("b") :
                   if "onclick" in val.attrs.keys() : 
                      vallabel = val.attrs["onclick"].split("\"")[3]
                      self.assertTrue( soup.find("span", {"id": vallabel}) )
               # Check for switching cells
               for val in soup.find_all(attrs={'class': 'toggler'}) :
                   if "onclick" in val.attrs.keys() :
                      switchval = val.attrs["onclick"].split("\"")[1]
                      if not soup.find("span",{"id": switchval + "_long"} ) : raise Exception("Generated html is invalid as could not find " + switchval + "_long")
                      if not soup.find("span",{"id": switchval + "_short"} ) : raise Exception("Generated html is invalid as could not find " + switchval + "_short")
