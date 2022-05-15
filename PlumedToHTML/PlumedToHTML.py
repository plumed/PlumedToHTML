import subprocess 
import os
import json
from pygments import highlight
from pygments.lexers import load_lexer_from_file
from pygments.formatters import load_formatter_from_file 
# Uncomment this line if it is required for tests  
# from pygments.formatters import HtmlFormatter

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
        cmd = ['plumed', 'driver', '--plumed', name + '.dat', '--natoms', '100000', '--parse-only', '--kt', '2.49','--shortcut-ofile', name + '.json']
        cmd = fix_mpi( nreplicas, cmd )
        plumed_out = subprocess.run(cmd, capture_output=True, text=True )
        if "PLUMED error" in plumed_out.stdout : broken = True

    # Check for shortcut file and build the modified input to read the shortcuts
    if os.path.exists( name + '.json' ) :
       # Read json file containing shortcuts
       f = open( name + '.json' )
       shortcutdata = json.load(f)
       f.close()
       # Put everything in to resolve the expansions.  We call this function recursively just in case there are shortcuts in shortcuts
       final_inpt = resolve_expansions( inpt, shortcutdata )
       # Remove the tempory files that we created
       os.remove( name + ".json") 
    else : final_inpt = inpt   

    # Create the lexer that will generate the pretty plumed input
    lexerfile = os.path.join(os.path.dirname(__file__),"PlumedLexer.py")
    plumed_lexer = load_lexer_from_file(lexerfile, "PlumedLexer" )
    # Get the plumed syntax file
    cmd = ['plumed', 'info', '--root']
    plumed_info = subprocess.run(cmd, capture_output=True, text=True ) 
    keyfile = plumed_info.stdout.strip() + "/json/syntax.json"
    plumed_formatter = load_formatter_from_file(lexerfile, "PlumedFormatter", keyword_file=keyfile, input_name=name )

    # Now generate html of input
    html = '<div style="width: 100%; float:left">\n'
    html += '<div style="width: 90%; float:left" id="value_details_' + name + '"> Click on the labels of the actions for more information on what each action computes </div>\n'
    if broken : html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/2.7-failed-red.svg" alt="tested on 2.7" /></div>\n'
    elif found_load : html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/with-LOAD-yellow.svg" alt="tested on 2.7" /></div>\n'
    elif found_fill : 
      html += "<button style=\"width: 10%; float:left\" type=\"button\" onmouseup=\'toggleDisplay(\"" + name + "\")\' onmousedown=\'toggleDisplay(\"" + name + "\")\'><img src=\"https://img.shields.io/badge/2.7-passing-green.svg\" alt=\"tested on 2.7\"/></button>\n"
    else : html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/2.7-passing-green.svg" alt="tested on 2.7" /></div>\n'
    html += "</div>\n"
    if found_fill : 
       # This creates the input with the __FILL__ 
       html += "<div id=\"" + name + "_short\">\n"
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( incomplete, plumed_lexer, plumed_formatter )
       html += "</div>\n"
       # This is the solution with the commplete input
       html += "<div style=\"display:none;\" id=\"" + name + "_long\">"
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( final_inpt, plumed_lexer, plumed_formatter )
    else : 
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( final_inpt, plumed_lexer, plumed_formatter )
 
    # Remove the tempory files that we created
    os.remove(name + ".dat")
    return html
 
def resolve_expansions( inpt, jsondata ) :
    # Stop expanding if we have reached the bottom 
    if len(jsondata.keys())==0 : return inpt

    incontinuation, final_inpt, clines = False, "", ""
    for line in inpt.splitlines() :        
        # Empty the buffer that holds the input for this line if we are not in a continuation
        if not incontinuation : clines = ""
        # Check for start and end of continuation
        if "..." in line and incontinuation : incontinuation=False
        elif "..." in line and not incontinuation : incontinuation=True
        # Build up everythign that forms part of input for one action
        clines += line + "\n"
        # Just continue if we don't have the full line
        if incontinuation : continue
        # Find the label of this line if it has one
        label = ""
        if clines.find(":") : label = clines.split(":")[0]
        elif clines.find("LABEL=") :
           afterlab = clines[clines.index("LABEL=") + len("LABEL="):]
           label = afterlab.split()[0]
        if len(label)>0 and label in jsondata :
           if "expansion" in jsondata[label] :
              final_inpt += "#SHORTCUT " + label + "\n"
              if "defaults" in jsondata[label] : final_inpt += "#NODEFAULT " + label + "\n" + clines
              else : final_inpt += clines
              # Add long version with defaults to input 
              if "defaults" in jsondata[label] and "..." in clines :
                 alldat, bef = clines.split("\n"), ""
                 for i in range(len(alldat)-2) : bef += alldat[i] + "\n"
                 final_inpt += "#DEFAULT " + label + "\n" + bef + jsondata[label]["defaults"] + "\n" + alldat[-2] + "\n#ENDDEFAULT " + label + "\n"
              elif "defaults" in jsondata[label]  : final_inpt += "#DEFAULT " + label + "\n" + clines.strip() + " " + jstondata[label]["defaults"] + "\n#ENDDEFAULT " + label + "\n"
              # Add stuff for long version of input in collapsible
              final_inpt += "#EXPANSION " + label + "\n# PLUMED interprets the command:\n"
              for gline in clines.splitlines() : final_inpt += "# " + gline + "\n"
              local_json = dict(jsondata[label]) 
              local_json.pop("expansion", "defaults" )
              final_inpt += "# as follows:\n" + resolve_expansions( jsondata[label]["expansion"], local_json )
              final_inpt += "#ENDEXPANSION " + label + "\n"
           elif "defaults" in jsondata[label] :
              final_inpt += "#NODEFAULT " + label + "\n" + clines
              if "defaults" in jsondata[label] and "..." in clines :
                 alldat, bef = clines.split("\n"), ""
                 for i in range(len(alldat)-2) : bef += alldat[i] + "\n"
                 final_inpt += "#DEFAULT " + label + "\n" + bef + jsondata[label]["defaults"] + "\n" + alldat[-2] + "\n#ENDDEFAULT " + label + "\n"
              elif "defaults" in jsondata[label]  : final_inpt += "#DEFAULT " + label + "\n" + clines.strip() + " " + jsondata[label]["defaults"] + "\n#ENDDEFAULT " + label + "\n"
        else : final_inpt += clines
    return final_inpt

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
    codes += '    min-width:400px;\n'
    codes += '    white-space: normal;\n'
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
    codes += 'function toggleDisplay(name) {\n'
    codes += '  var short_div = document.getElementById(name + "_short");\n'
    codes += '  var long_div = document.getElementById(name + "_long");\n'
    codes += '  if( short_div.style.display === "none" ) {\n'
    codes += '      short_div.style.display = "block";\n'
    codes += '      long_div.style.display = "none";\n'
    codes += '  } else { \n'
    codes += '      short_div.style.display = "none";\n'
    codes += '      long_div.style.display = "block";\n'  
    codes += '  }\n'
    codes += '}\n'
    codes += '</script>\n'
    return codes
