from unittest import TestCase

import os
import json
import PlumedToHTML
from bs4 import BeautifulSoup

class TestPlumedToHTML(TestCase):
   def testBasicOutput(self) :
       # Open the json file and read it in
       f = open("tdata/tests.json")
       tests = json.load(f)
       f.close()

       # Now run over all the inputs in the json
       for item in tests["regtests"] :
           with self.subTest(item=item):
                print("INPUT", item["index"], item["input"] )
                actions = set({})
                out = PlumedToHTML.test_and_get_html( item["input"], "plinp" + str(item["index"]), actions=actions )
                self.assertTrue( actions==set(item["actions"]) ) 
                self.assertTrue( PlumedToHTML.compare_to_reference( out, item ) )
                soup = BeautifulSoup( out, "html.parser" )
                # Check the badges 
                out_badges = soup.find_all("img")
                self.assertTrue( len(out_badges)==len(item["badges"]) )
                for i in range(len(out_badges)) :
                    if item["badges"][i]=="pass" : self.assertTrue( out_badges[i].attrs["src"].find("passing")>0 ) 
                    elif item["badges"][i]=="fail" : self.assertTrue( out_badges[i].attrs["src"].find("failed")>0 )
                    elif item["badges"][i]=="load" : self.assertTrue( out_badges[i].attrs["src"].find("with-LOAD")>0 )
                    elif item["badges"][i]=="incomplete" : self.assertTrue( out_badges[i].attrs["src"].find("incomplete")>0 )
