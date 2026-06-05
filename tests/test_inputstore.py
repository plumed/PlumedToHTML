from unittest import TestCase

import os
import json
import PlumedToHTML
from bs4 import BeautifulSoup

class TestPlumedToHTML(TestCase):
   def testBasicOutput(self) :
       # Open the json file and read it in
       f = open("tdata/inputstoretests.json")
       tests = json.load(f)
       f.close()

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item):
                print("INPUT", item["index"], item["input"] )
                mystore = []
                out = PlumedToHTML.get_html( item["input"], "plinp" + str(item["index"]), "plinp" + str(item["index"]), ("master",), (True,), ("plumed",), input_store=mystore )
                print( "OUTPUT", mystore ) 
                print( "AGAINST", item["output"] )
                self.assertTrue( mystore==item["output"] )
