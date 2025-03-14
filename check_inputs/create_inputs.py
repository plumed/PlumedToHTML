from pygments.styles import get_style_by_name
from pygments.formatters import HtmlFormatter
import os
import json
import PlumedToHTML

# Output css file for codehighlighting
ofile = open("codehilite.css", "w+")
ofile.write( HtmlFormatter(cssclass="codehilite", style='colorful').get_style_defs() )
ofile.close()

print("<html>")
print('<meta charset="utf-8">')
print('<link rel="stylesheet" type="text/css" href="./codehilite.css">')
print('<meta name="viewport" content="width=device-width">')
print('<title>Example tutorial</title>')
print('<meta name="description" content="PLUMED website"/>')
print('<meta name="viewport" content="width=device-width, initial-scale=1">')
print('<meta name="theme-color" content="#157878">')
print('<link href=\'https://fonts.googleapis.com/css?family=Open+Sans:400,700\' rel=\'stylesheet\' type=\'text/css\'>')
print('<link rel="stylesheet" href="https://www.plumed.org//assets/css/style.css?v=9dd2bd3d9ee4823fb5d3485bda969afbaa1ba8d4">')
print('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">')
print('<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/jszip-2.5.0/dt-1.10.18/b-1.5.6/b-flash-1.5.6/b-html5-1.5.6/datatables.min.css"/>')
print('<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/jq-3.3.1/jszip-2.5.0/dt-1.10.18/b-1.5.6/b-flash-1.5.6/b-html5-1.5.6/datatables.min.css"/>')
print('<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/pdfmake.min.js"></script>')
print('<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/vfs_fonts.js"></script>')
print('<script type="text/javascript" src="https://cdn.datatables.net/v/dt/jq-3.3.1/jszip-2.5.0/dt-1.10.18/b-1.5.6/b-flash-1.5.6/b-html5-1.5.6/datatables.min.js"></script>')
print('<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>')
print('<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>')
print('</head>')
print('<body>')
print('<section class="page-header">')
print('<a href="https://github.com/plumed/plumed2"><img style="position:absolute; top:10px; right:100px; width:50px" src="https://www.plumed.org//Octocat.png" title="Get development version"></a>')
print('<a href="https://github.com/plumed/plumed2/releases/download/v2.8.0/plumed-2.8.0.tgz"><img style="position:absolute; top:10px; right:40px; width:40px" src="https://www.plumed.org//arrow.png" title="Get latest release"></a>')
print('<a class="site-title" href="http://www.plumed.org"><img width="220" src="pigeon-teacher.png"></a>')
print('<h1 class="project-name">PLUMED</h1>')
print('<h2 class="project-tagline">The community-developed PLUgin for MolEcular Dynamics</h2>')
print('</section>')
print('<section class="main-content">', flush=True)
# Putting this here You can see render the page while it is being generated
print( PlumedToHTML.get_html_header() )
f = open("./tdata/tests.json")
tests = json.load(f)
f.close()

for item in tests["regtests"] :
    actions = set({})
    out = PlumedToHTML.test_and_get_html( item["input"], "plinp" + str(item["index"]), actions=actions )
    
    print(f"<h3>Input number {item['index']}</h3>")
    #this visualizes the "from-to" and it is more clear to eye-check what is going on
    print("<pre>")
    print(item["input"])
    print("</pre>")
    print( out )

f = open("./tdata/cltooltests.json")
tests = json.load(f)
f.close()

for item in tests["regtests"] :
    out = PlumedToHTML.get_cltoolarg_html( item["input"], "clinp" + str(item["index"]), ("plumed",) )
    #this visualizes the "from-to" and it is more clear to eye-check what is going on
    print(f"<h3>CL tool input number {item['index']}</h3>")
    print("<pre>")
    print(item["input"])
    print("</pre>")
    print( out )

print('</section>')
print('</body>')
print('</html>')
