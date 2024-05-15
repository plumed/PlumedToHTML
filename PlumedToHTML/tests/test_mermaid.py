from unittest import TestCase

import os
import subprocess
from PlumedToHTML import get_mermaid

class TestPlumedToHTMLMermaid(TestCase):
   def testNormalGraph(self) :
       inpt="d1: DISTANCE ATOMS=1,2\n PRINT ARG=d1 FILE=colvar"
       mermaid_this = get_mermaid( "plumed", inpt, False )
       iff = open("test_mermaid.dat","w+")
       iff.write(inpt)
       iff.close()
       cmd = ['plumed', 'show_graph', '--plumed', 'test_mermaid.dat', '--out', 'test_mermaid.md']
       plumed_out = subprocess.run(cmd, capture_output=True, text=True )
       mf = open("test_mermaid.md")
       mermaid_pp = mf.read()
       mf.close()
       os.remove("test_mermaid.dat")
       os.remove("test_mermaid.md")
       self.assertTrue( mermaid_pp == mermaid_this )

   def testForceGraph(self) :
       inpt="d1: DISTANCE ATOMS=1,2\n rr: RESTRAINT ARG=d1 KAPPA=10 AT=1"
       mermaid_this = get_mermaid( "plumed", inpt, True )
       iff = open("test_mermaid.dat","w+")
       iff.write(inpt)
       iff.close()
       cmd = ['plumed', 'show_graph', '--plumed', 'test_mermaid.dat', '--out', 'test_mermaid.md', '--force']
       plumed_out = subprocess.run(cmd, capture_output=True, text=True )
       mf = open("test_mermaid.md")
       mermaid_pp = mf.read()
       mf.close()
       os.remove("test_mermaid.dat")
       os.remove("test_mermaid.md")
       self.assertTrue( mermaid_pp == mermaid_this )
       


