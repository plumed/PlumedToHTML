import subprocess 
import os
import json
from pygments import highlight
from pygments.lexers import load_lexer_from_file
from pygments.formatters import load_formatter_from_file 
# Uncomment this line if it is required for tests  
# from pygments.formatters import HtmlFormatter

def test_plumed( executible, filename, shortcutfile=[] ) :
    """
        Test if plumed can parse this input file

        This function can be used to test if PLUMED can parse an input file.  It calls plumed using subprocess

        Keyword arguments:
        executible   -- A string that contains the command for running plumed
        filename     -- A string that contains the name of the plumed input file to parse
        shortcutfile -- The file on which to output the json file containing the expansed shortcuts.  If not present this is not output 
    """
    # Read in the plumed inpt
    nreplicas, ifile = 1, open( filename )
    for line in ifile.readlines() :
        if "#SETTINGS" in line :
            for word in line.split() :
                if "NREPLICAS=" in word : nreplicas = word.replace("NREPLICAS=","")
        if "LOAD" in line : return True 
    ifile.close()
    cmd = [executible, 'driver', '--plumed', filename, '--natoms', '100000', '--parse-only', '--kt', '2.49']
    # Add everything to ensure we can run with replicas if needs be
    if int(nreplicas)>1 :
       # This is a crappy fudge to hopefully get tests with replicas -- I think PLUMED is not outputting the json file when it is run in parallel
       if len(shortcutfile)>0 :
          serialcmd = [executible, 'driver', '--plumed', filename, '--natoms', '100000', '--parse-only', '--kt', '2.49', '--shortcut-ofile', shortcutfile] 
          plumed_out = subprocess.run(serialcmd, capture_output=True, text=True ) 
       # This is the end of my crappy fudge
       cmd.insert(0,nreplicas)
       cmd.insert(0,"-np"),
       cmd.insert(0,"mpirun")
       cmd.append("--multi")
       cmd.append(nreplicas)
    # Add the shortcutfile output if the user has asked for it
    elif len(shortcutfile)>0 :
       cmd.append('--shortcut-ofile')
       cmd.append(shortcutfile)
    plumed_out = subprocess.run(cmd, capture_output=True, text=True )
    if "PLUMED: ERROR" in plumed_out.stdout : return True
    return False

def get_html( inpt, name ) :
    """
       Generate the html representation of a PLUMED input file

       The html representation of a PLUMED input file has tooltips that 
       tell you what the keywords represent, a badge that shows whether the input
       works and clickable labels that provide information about the quantities that 
       are calculated.  This function uses test_plumed to check if the plumed inpt can be parsed.

       Keyword arguments:
       inpt -- A string containing the PLUMED input"
       name -- The name to use for this input in the html
    """
    
    # Check if there is a LOAD command in the input
    found_load = "LOAD " in inpt
 
    # If we find the fill command then split up the input file to find the solution
    incomplete = ""
    if "__FILL__" in inpt :
       insolution, complete = False, ""
       for line in inpt.splitlines() :
           if "#SOLUTION" in line : insolution=True
           elif insolution : complete += line + "\n"
           elif not insolution : incomplete += line + "\n"
       inpt = complete

    # Write the plumed input to a file
    iff = open( name + ".dat", "w+")
    iff.write(inpt + "\n")
    iff.close()

    # Run plumed to test code
    if not found_load : broken = test_plumed( "plumed", name + ".dat", shortcutfile=name + '.json' )

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
    if found_load :
       html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/with-LOAD-yellow.svg" alt="tested on 2.7" /></div>\n'
    elif broken :
       html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/2.7-failed-red.svg" alt="tested on 2.7" /></div>\n'
    elif len(incomplete)>0 : 
       html += "<button style=\"width: 10%; float:left\" type=\"button\" onmouseup=\'toggleDisplay(\"" + name + "\")\' onmousedown=\'toggleDisplay(\"" + name + "\")\'><img src=\"https://img.shields.io/badge/2.7-passing-green.svg\" alt=\"tested on 2.7\"/></button>\n"
    else : 
       html += '<div style="width: 10%; float:left"><img src=\"https://img.shields.io/badge/2.7-passing-green.svg" alt="tested on 2.7" /></div>\n'
    html += "</div>\n"
    if len(incomplete)>0 : 
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
        if "LABEL=" in clines :
           afterlab = clines[clines.index("LABEL=") + len("LABEL="):]
           label = afterlab.split()[0]
        elif clines.find(":") : label = clines.split(":")[0].strip()
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
              elif "defaults" in jsondata[label]  : final_inpt += "#DEFAULT " + label + "\n" + clines.strip() + " " + jsondata[label]["defaults"] + "\n#ENDDEFAULT " + label + "\n"
              # Add stuff for long version of input in collapsible
              final_inpt += "#EXPANSION " + label + "\n# PLUMED interprets the command:\n"
              for gline in clines.splitlines() : final_inpt += "# " + gline + "\n"
              local_json = dict(jsondata[label]) 
              local_json.pop("expansion", "defaults" )
              final_inpt += "# as follows:\n" + resolve_expansions( jsondata[label]["expansion"], local_json )
              final_inpt += "#ENDEXPANSION " + label + "\n"
           elif "defaults" in jsondata[label] :
              final_inpt += "#NODEFAULT " + label + "\n" + clines
              if "..." in clines :
                 alldat, bef = clines.split("\n"), ""
                 for i in range(len(alldat)-2) : bef += alldat[i] + "\n"
                 final_inpt += "#DEFAULT " + label + "\n" + bef + jsondata[label]["defaults"] + "\n" + alldat[-2] + "\n#ENDDEFAULT " + label + "\n"
              else : final_inpt += "#DEFAULT " + label + "\n" + clines.strip() + " " + jsondata[label]["defaults"] + "\n#ENDDEFAULT " + label + "\n"
        else : final_inpt += clines
    return final_inpt

def get_html_header() :
    """
       Get the information that needs to go in the header of the html file to make the interactive PLUMED
       inputs work
    """
    headerfilename = os.path.join(os.path.dirname(__file__),"assets/header.html")
    hfile = open( headerfilename )
    codes = hfile.read()
    hfile.close()
    return codes
