from unittest import TestCase

import os
import json
import PlumedToHTML

class TestPlumedToHTML(TestCase):
   def testBasicOutput(self) :
       # Open the json file and read it in
       f = open("tdata/tests.json")
       tests = json.load(f)
       f.close()

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item):
                out = PlumedToHTML.get_html( item["input"], "plinp" + str(item["index"]) )
                print( item["input"] )
                print( out )
                self.assertTrue( out==item["output"] )

   def testHeader(self) :
       headerfilename = os.path.join(os.path.dirname(__file__),"../assets/header.html")
       hfile = open( headerfilename )
       codes = hfile.read()
       hfile.close()
       self.assertTrue( codes==PlumedToHTML.get_html_header() )
