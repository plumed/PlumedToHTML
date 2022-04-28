import subprocess 
import os
from pygments import highlight
from pygments.lexers import load_lexer_from_file
from pygments.formatters import load_formatter_from_file, HtmlFormatter

def fix_mpi( nreplicas, cmd ) :
    """
       Take a cmd string for plumed and mpi specifications if multiple replicas are being used
 
       Keywords argumnets:
       npreplicas -- the number of replicas that are being used
       cmd - a list containing the command to call plumed
    """
    if int(nreplicas)>1 :
       cmd.insert(0,nreplicas)
       cmd.insert(0,"-np"), 
       cmd.insert(0,"mpirun")
       cmd.append("--multi")
       cmd.append(nreplicas)
    return cmd

def get_html( inpt, name ) :
    """
       Generate the html representation of a PLUMED input file

       The html representation of a PLUMED input file has tooltips that 
       tell you what the keywords represent, a badge that shows whether the input
       works and clickable labels that provide information about the quantities that 
       are calculated.  This function called plumed using subprocess.

       Keyword arguments:
       inpt -- A string containing the PLUMED input file"
       name -- The name to use for this input in the html
    """

    print("IN GET HTML", name )
    nreplicas, found_load, found_fill = 1, False, False
    # Find the settinngs for running this command and check that the input is complete
    for line in inpt.splitlines() :
        if "#SETTINGS" in line :
            for word in line.split() :
                if "NREPLICAS=" in word : nreplicas = word.replace("NREPLICAS=","")
        if "LOAD" in line : found_load = True
        if "__FILL__" in line : found_fill = True
 
    # If we find the fill command then split up to find the solution
    incomplete = ""
    if found_fill :
       insolution, complete = False, ""
       for line in inpt.splitlines() :
           if "#SOLUTION" in line : insolution=True
           elif insolution : complete += line + "\n"
           elif not insolution : incomplete += line + "\n"
       inpt = complete

    # Write the plumed input to a file
    iff = open( name + ".dat", "w+")
    iff.write(inpt)
    iff.close()

    # Run plumed to test code
    broken = False
    if not found_load : 
        cmd = ['plumed', 'driver', '--plumed', name + '.dat', '--natoms', '100000', '--parse-only', '--kt', '2.49','--full-input-ofile', name + '_long.dat']
        cmd = fix_mpi( nreplicas, cmd )
        plumed_out = subprocess.run(cmd, capture_output=True, text=True )
        if "PLUMED error" in plumed_out.stdout : broken = True

    # Create the lexer that will generate the pretty plumed input
    plumed_lexer = load_lexer_from_file("PlumedLexer.py", "PlumedLexer" )
    plumed_formatter = load_formatter_from_file("PlumedLexer.py", "PlumedFormatter", keyword_file="plumed_dict.json", input_name=name )

    # Now generate html of input
    html = '<div style="width: 100%; float:left">\n'
    if found_fill :
       html += '<div style=\"width: 80%; float:left\" id=\"value_details_' + name + '\"> Click on the labels of the actions for more information on what each action computes </div>\n'
       html += "<div style=\"width: 10%; float:left\"><button type=\"button\" id=\"" + name + "_button\" onclick=\'swapInput(\"" + name + "\")\'>show solution</button></div>\n"
    elif os.path.isfile( name + '_long.dat') : 
       html += '<div style=\"width: 80%; float:left\" id=\"value_details_' + name + '\"> Click on the labels of the actions for more information on what each action computes </div>\n'
       html += "<div style=\"width: 10%; float:left\"><button type=\"button\" id=\"" + name + "_button\" onclick=\'swapInput(\"" + name + "\")\'>contract shortcuts</button></div>\n"
    else : html += '<div style="width: 90%; float:left" id="value_details_' + "inpt" + '"> Click on the labels of the actions for more information on what each action computes </div>\n'
    if broken : html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/2.7-failed-red.svg" alt="tested on 2.7" /></div>\n'
    elif found_load : html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/with-LOAD-yellow.svg" alt="tested on 2.7" /></div>\n'
    else : html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/2.7-passing-green.svg" alt="tested on 2.7" /></div>\n'
    html += "</div>\n"
    if found_fill : 
       html += highlight( inpt, plumed_lexer, plumed_formatter ) 
    elif os.path.isfile( name + '_long.dat') : 
       "<div style=\"width: 100%; float:left\" id=\"input_"<<egname<<"\"></div>\n"
       # Write an extra pre to make sure the html after the example is put in the right place on the page
       html += "<pre style=\"width: 97%;\" class=\"fragment\"></pre>\n"
       html += "<script type=\"text/javascript\">\n"
       html += "if (window.addEventListener) { // Mozilla, Netscape, Firefox\n"
       html += "    window.addEventListener('load', "+ name + "Load, false);\n"
       html += "} else if (window.attachEvent) { // IE\n"
       html += "    window.attachEvent('onload', " + name + "Load);\n"
       html += "}\n"
       html += "function " + name + "Load(event) {\n"
       html += "       swapInput(\"" + name + "\");\n"
       html += "}\n"
       html += "</script>\n"
       html += "<div style=\"display:none;\" id=\"" + name + "short\">\n"
       # html += highlight( inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( inpt, plumed_lexer, plumed_formatter )
       html += "</div>\n"
       html += "<div style=\"display:none;\" id=\"" + name + "long\">"
       if2 = open( name + '_long.dat' )
       inpt2 = if2.read()
       if2.close()
       # html += highlight( inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( inpt2, plumed_lexer, plumed_formatter )
    else : 
       # html += highlight( inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( inpt, plumed_lexer, plumed_formatter )
 
    # Remove the tempory files that we created
    os.remove(name + ".dat")
    return html
 
def get_html_header() :
    """
       Get the information that needs to go in the header of the html file to make the interactive PLUMED
       inputs work
    """
    codes = '<style>\n'
    # Style for PLUMED inputs taken from Doxygen
    codes += 'pre.fragment {\n'
    codes += '    border: 1px solid #C4CFE5;\n'
    codes += '    background-color: #FBFCFD;\n'
    codes += '    padding: 4px 6px;\n'
    codes += '    margin: 4px 8px 4px 2px;\n'
    codes += '    overflow: auto;\n'
    codes += '    word-wrap: break-word;\n'
    codes += '    font-size:  9pt;\n'
    codes += '    line-height: 125%;\n'
    codes += '    font-family: monospace, fixed;\n'
    codes += '    font-size: 105%;\n'
    codes += '}\n'
    codes += '.tooltip {\n'
    codes += '    display:inline-block;\n'
    codes += '    position:relative;\n'
    codes += '    border-bottom:1px dotted #666;\n'
    codes += '    text-align:left;\n'
    codes += '}\n'
    codes += '.tooltip .right {\n'
    codes += '    min-width:200px;\n'
    codes += '    top:50%;\n'
    codes += '    left:100%;\n'
    codes += '    margin-left:20px;\n'
    codes += '    transform:translate(0, -50%);\n'
    codes += '    padding:10px 20px;\n'
    codes += '    color:#444444;\n'
    codes += '    background-color:#EEEEEE;\n'
    codes += '    font-weight:normal;\n'
    codes += '    font-size:13px;\n'
    codes += '    border-radius:8px;\n'
    codes += '    position:absolute;\n'
    codes += '    z-index:99999999;\n'
    codes += '    box-sizing:border-box;\n'
    codes += '    box-shadow:0 1px 8px rgba(0,0,0,0.5);\n'
    codes += '    display:none;\n'
    codes += '}\n'
    codes += '.tooltip:hover .right {\n'
    codes += '    display:block;\n'
    codes += '}\n'
    codes += '.tooltip .right i {\n'
    codes += '    position:absolute;\n'
    codes += '    top:50%;\n'
    codes += '    right:100%;\n'
    codes += '    margin-top:-12px;\n'
    codes += '    width:12px;\n'
    codes += '    height:24px;\n'
    codes += '    overflow:hidden;\n'
    codes += '}\n'
    codes += '.tooltip .right i::after {\n'
    codes += '    content:'';\n'
    codes += '    position:absolute;\n'
    codes += '    width:12px;\n'
    codes += '    height:12px;\n'
    codes += '    left:0;\n'
    codes += '    top:50%;\n'
    codes += '    transform:translate(50%,-50%) rotate(-45deg);\n'
    codes += '    background-color:#EEEEEE;\n'
    codes += '    box-shadow:0 1px 8px rgba(0,0,0,0.5);\n'
    codes += '}\n'
    codes += '</style>\n'
    codes += '<script>\n'
    codes += 'var redpath="";\n'
    codes += 'function showPath(eg,name) {\n'
    codes += '  var i; var y = document.getElementsByName(redpath);\n'
    codes += '  for (i=0; i < y.length; i++ ) { y[i].style.color="black"; }\n'
    codes += '  var x = document.getElementsByName(name); redpath=name;\n'
    codes += '  for (i = 0; i < x.length; i++) { x[i].style.color="red"; }\n'
    codes += '  var valid="value_details_".concat(eg);\n'
    codes += '  var valueField = document.getElementById(valid);\n'
    codes += '  var dataField = document.getElementById(name);\n'
    codes += '  valueField.innerHTML = dataField.innerHTML;\n'
    codes += '}\n'
    codes += 'function swapInput(name) {\n'
    codes += '  var btn = document.getElementById(name + "_button");\n'
    codes += '  var mydiv = document.getElementById("input_" + name);\n'
    codes += '  if( btn.textContent=="expand shortcuts" ) {\n'
    codes += '      btn.textContent = "contract shortcuts";\n'
    codes += '      var dataField = document.getElementById(name + "long");\n'
    codes += '      mydiv.innerHTML = dataField.innerHTML;\n'
    codes += '  } else if( btn.textContent=="contract shortcuts" ) {\n'
    codes += '      btn.textContent = "expand shortcuts";\n'
    codes += '      var dataField = document.getElementById(name + "short");\n'
    codes += '      mydiv.innerHTML = dataField.innerHTML;\n'
    codes += '  }\n'
    codes += '}\n'
    codes += '</script>\n'
    return codes
