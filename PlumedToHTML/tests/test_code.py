from unittest import TestCase

import json
import PlumedToHTML
from lxml.html.diff import htmldiff

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
                self.assertTrue( out==item["output"] )
