from unittest import TestCase

import PlumedToHTML


class TestPlumedArguments(TestCase):
  def testReadKeywords(self):
    inpt = """
```plumed
d1: DISTANCE ATOMS=1,2 
PRINT ARG=d1 FILE=colvar
```
"""
    actions = set({})
    keyset = set({"ATOMS", "COMPONENTS"})
    with open("check_keywords_file", "w") as ofile:
      PlumedToHTML.processMarkdownString(
        inpt,
        "check_keyword",
        ("plumed",),
        ("master",),
        actions,
        ofile,
        checkaction="DISTANCE",
        checkactionkeywords=keyset,
      )
    self.assertTrue(keyset == set({"COMPONENTS"}))

    keyset = set({"ARG", "FILE"})
    with open("check_keywords_file", "w") as ofile:
      PlumedToHTML.processMarkdownString(
        inpt,
        "check_keyword",
        ("plumed",),
        ("master",),
        actions,
        ofile,
        checkaction="PRINT",
        checkactionkeywords=keyset,
      )
    self.assertTrue(len(keyset) == 0)

    inpt = """
```plumed
d1: DISTANCE ATOMS1=1,2 ATOMS2=3,4 
PRINT ARG=d1 FILE=colvar
```
"""
    actions = set({})
    keyset = set({"ATOMS", "COMPONENTS"})
    with open("check_keywords_file", "w") as ofile:
      PlumedToHTML.processMarkdownString(
        inpt,
        "check_keyword",
        ("plumed",),
        ("master",),
        actions,
        ofile,
        checkaction="DISTANCE",
        checkactionkeywords=keyset,
      )
    self.assertTrue(keyset == set({"COMPONENTS"}))

    inpt = """
```plumed
# Define two groups of atoms
g: GROUP ATOMS=1-5
h: GROUP ATOMS=6-20
  
# Calculate the CONTACT_MATRIX for the atoms in group g
cg: CONTACT_MATRIX GROUP=g SWITCH={RATIONAL R_0=0.1}

# Calculate the CONTACT_MATRIX for the atoms in group h
ch: CONTACT_MATRIX GROUP=h SWITCH={RATIONAL R_0=0.2}

# Calculate the CONTACT_MATRIX between the atoms in group g and group h
cgh: CONTACT_MATRIX GROUPA=g GROUPB=h SWITCH={RATIONAL R_0=0.15}

# Now calculate the contact matrix between the atoms in group h and group h
# Notice this is just the transpose of cgh
cghT: TRANSPOSE ARG=cgh

# And concatenate the matrices together to construct the adjacency matrix between the
# adjacency matrices
m: CONCATENATE ...
 MATRIX11=cg MATRIX12=cgh
 MATRIX21=cghT MATRIX22=ch
...
```
"""

    actions = set({})
    keyset = set({"MATRIX"})
    with open("check_keywords_file", "w") as ofile:
      PlumedToHTML.processMarkdownString(
        inpt,
        "check_keyword",
        ("plumed",),
        ("master",),
        actions,
        ofile,
        checkaction="CONCATENATE",
        checkactionkeywords=keyset,
      )
    print("final keyset", keyset)
    self.assertTrue(keyset == set({}))
