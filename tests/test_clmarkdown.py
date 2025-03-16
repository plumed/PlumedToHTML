from unittest import TestCase

import os
import json
import PlumedToHTML
from bs4 import BeautifulSoup

class TestPlumedToHTML(TestCase):
   def testBasicOutput(self) :
       # Run over the checks on the command line tools
       f = open("tdata/cltooltests.json")
       cltests = json.load(f)
       f.close()

       # Now run over all the inputs in the json
       n=1
       for item in cltests["regtests"] :
           with self.subTest(item=item):
                print("INPUT", item["index"], item["input"] )
                with open("testmarkdown" + str(n) +".md", "w") as of :
                     of.write("# TEST MARKDOWN \n\n")
                     of.write("Some text before DISTANCE \n")
                     of.write("```plumed`\n")
                     of.write( item["input"] + "\n")
                     of.write("```\n")
                     of.write("Some text after \n")
                actions = set()
                PlumedToHTML.processMarkdown( "testmarkdown" + str(n) +".md", ("plumed",), ("master",), actions )
                with open("testmarkdown" + str(n) +".md", "r") as f : inp = f.read()
                out, inhtml = "", False
                for line in inp.splitlines() :
                    if inhtml and "{% endraw %}" in line : inhtml = False
                    elif inhtml : out += line + "\n"
                    elif "{% raw %}" in line : inhtml = True
                self.assertTrue( PlumedToHTML.compare_to_reference( out, item ) )
                n=n+1

       # Run over the the checks on the command line input files
       f = open("tdata/clfiletests.json")
       filetests = json.load(f)
       f.close()

       for item in filetests["regtests"] :
           with self.subTest(item=item):
                print("INPUT", item["index"], item["input"] )
                with open("testmarkdown" + str(n) +".md", "w") as of :
                     of.write("# TEST MARKDOWN \n\n")
                     of.write("Some text before DISTANCE \n")
                     of.write("```plumed`\n")
                     of.write( item["input"] + "\n")
                     of.write("```\n")
                     of.write("Some text after \n")
                actions = set()
                PlumedToHTML.processMarkdown( "testmarkdown" + str(n) +".md", ("plumed",), ("master",), actions )
                with open("testmarkdown" + str(n) +".md", "r") as f : inp = f.read()
                out, inhtml = "", False
                for line in inp.splitlines() :
                    if inhtml and "{% endraw %}" in line : inhtml = False
                    elif inhtml : out += line + "\n"
                    elif "{% raw %}" in line : inhtml = True
                self.assertTrue( PlumedToHTML.compare_to_reference( out, item ) )
                n=n+1

