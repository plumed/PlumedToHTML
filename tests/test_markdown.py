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
       n=1
       for item in tests["regtests"] :
           with self.subTest(item=item):
                print("INPUT", item["index"], item["input"] )
                if "__FILL__" in item["input"] : continue
                with open("testmarkdown" + str(n) +".md", "w") as of :
                     of.write("# TEST MARKDOWN \n\n")
                     of.write("Some text before DISTANCE \n")
                     of.write("```plumed`\n")
                     of.write( item["input"] + "\n")
                     of.write("```\n")
                     of.write("Some text after \n")
                actions = set()
                PlumedToHTML.processMarkdown( "testmarkdown" + str(n) +".md", ("plumed",), ("master",), actions )
                self.assertTrue( actions==set(item["actions"]) ) 
                with open("testmarkdown" + str(n) +".md", "r") as f : inp = f.read()
                out, inhtml = "", False
                for line in inp.splitlines() :
                    if inhtml and "{% endraw %}" in line : inhtml = False
                    elif inhtml : out += line + "\n"
                    elif "{% raw %}" in line : inhtml = True 
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
                n=n+1

       with open("testmarkdown" + str(n) +".md", "w") as of :
            of.write("# TEST MARKDOWN \n\n")
            of.write("Some text before \n")
            of.write("```plumed`\n")
            of.write("#SOLUTIONFILE=tdata/solution.dat\n")
            of.write("d: DISTANCE __FILL__=1,2\n")
            of.write("```\n")
            of.write("Some text after \n")
       actions = set() 
       PlumedToHTML.processMarkdown( "testmarkdown" + str(n) +".md", ("plumed",), ("master",), actions )
       self.assertTrue( actions==set(["DISTANCE"]) )


   def testHeader(self) :
       #checks that the header has been installed
       #assuming that we are in /tests
       headerfilename = os.path.join(os.path.dirname(__file__),"../src/PlumedToHTML/assets/header.html")
       hfile = open( headerfilename )
       codes = hfile.read()
       hfile.close()
       self.assertTrue( codes==PlumedToHTML.get_html_header() )

   def testJavascriptAndCSS(self) : 
       headerfilename = os.path.join(os.path.dirname(__file__),"../src/PlumedToHTML/assets/header.html")
       hfile = open( headerfilename )
       codes = hfile.read()
       hfile.close()
       reference = "<style>\n"
       reference += PlumedToHTML.get_css()
       reference += "</style>\n<script>\n"
       reference += PlumedToHTML.get_javascript()
       reference += "</script>\n"
       print( reference )
       self.assertTrue( codes==reference )
