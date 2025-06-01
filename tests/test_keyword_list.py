from unittest import TestCase

import os
import json
import PlumedToHTML

class TestPlumedArguments(TestCase):
   def testReadKeywords(self) : 
       inpt = """
```plumed
d1: DISTANCE ATOMS=1,2 
PRINT ARG=d1 FILE=colvar
```
"""
       actions = set({})
       keyset = set({"ATOMS","COMPONENTS"})
       with open("check_keywords_file", "w") as ofile :
           PlumedToHTML.processMarkdownString( inpt, "check_keyword", ("plumed",), ("master",), actions, ofile, checkaction="DISTANCE", checkactionkeywords=keyset )
       self.assertTrue( keyset==set({"COMPONENTS"}) )
       
       keyset = set({"ARG","FILE"})
       with open("check_keywords_file", "w") as ofile :
           PlumedToHTML.processMarkdownString( inpt, "check_keyword", ("plumed",), ("master",), actions, ofile, checkaction="PRINT", checkactionkeywords=keyset )
       self.assertTrue( len(keyset)==0 )

       inpt = """
```plumed
d1: DISTANCE ATOMS1=1,2 ATOMS2=3,4 
PRINT ARG=d1 FILE=colvar
```
"""
       actions = set({})
       keyset = set({"ATOMS","COMPONENTS"})
       with open("check_keywords_file", "w") as ofile :
           PlumedToHTML.processMarkdownString( inpt, "check_keyword", ("plumed",), ("master",), actions, ofile, checkaction="DISTANCE", checkactionkeywords=keyset )
       self.assertTrue( keyset==set({"COMPONENTS"}) )
