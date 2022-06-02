[![CI](https://github.com/plumed/PlumedToHTML/actions/workflows/main.yml/badge.svg)](https://github.com/plumed/PlumedToHTML/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/plumed/PlumedToHTML/branch/main/graph/badge.svg?token=ODA9N9MEGP)](https://codecov.io/gh/plumed/PlumedToHTML)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/plumed/PlumedToHTML.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/plumed/PlumedToHTML/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/plumed/PlumedToHTML.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/plumed/PlumedToHTML/context:python)
[![PyPI version](https://badge.fury.io/py/PlumedToHTML.svg)](https://badge.fury.io/py/PlumedToHTML)

# PlumedToHTML

This is a Python implementation that allows you to generate pretified PLUMED input files that can be included in HTML documents.  These pretified inputs have the following features:
 
* There is a badge that shows whether PLUMED is able to parse the input or not.
* When you hover over the names of actions tooltips appear to describe them that contain links to the corresponding pages in the PLUMED documentation.
* When you hover over the keyword name a tooltip explains the meaning of that particular keyword.
* If you click on the label for an action an explanation of that quantity that is stored in that label is given.  The way the quantity is used in the rest of the calculation is given.
* If shortcuts are used and actions read in things that do not appear in the input you have the option to see what actions are read in by PLUMED.  You can thus get insight into how methods are implemented in PLUMED.
* If some action has parameters that are set to default values you have the option to see what the default values of these parameters are. 

N.B. This script uses subprocess to call PLUMED __If you use this script PLUMED must be available in your path__

# Documentation

You can install this script by using the command:

````
pip install plumedToHTML
````

You can then use it within a python script by using the command:

````
from PlumedToHTML import get_html, get_html_header
````

The function `get_html` takes two arguments:

* The first argument is a string that contains the PLUMED input you want to get the html for.
* The second argument is a label that is used to refer to the input.  __If you have multiple PLUMED inputs on one page they all must have different labels__

This function returns a string that contains the PLUMED input html to include in your page.

The function `get_html_header` returns some javascript functions and css definitions that must be included in the header of the html page.  These functions and css instructions control how the PLUMED inputs appear.
