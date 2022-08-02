import subprocess 
import os
import re
import json
import pathlib
import zipfile
from contextlib import contextmanager
from pygments import highlight
from pygments.lexers import load_lexer_from_file
from pygments.formatters import load_formatter_from_file 
# Uncomment this line if it is required for tests  
#from pygments.formatters import HtmlFormatter

def zip(path):
    """ Zip a path removing the original file """
    with zipfile.ZipFile(path + ".zip", "w") as f_out:
        f_out.write(path)
    os.remove(path)

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def test_and_get_html( inpt, name ) :
    """
        Test if the plumed input is broken and generate the html syntax

        This function wraps test_plumed and get_html

        Keyword arguments:
        inpt -- A string containing the PLUMED input
        name -- The name to use for this input in the html
    """
    # Check if this is to be included by another input
    filename, keepfile = name + ".dat", False
    for line in inpt.splitlines() :
        if "#SETTINGS" in line :
           for word in line.split() :
               if "FILENAME=" in word : filename, keepfile = word.replace("FILENAME=",""), True
    # Manage incomplete inputs
    test_inpt, incomplete = manage_incomplete_inputs( inpt )
    # Write the plumed input to a file
    iff = open( filename, "w+")
    iff.write(test_inpt + "\n")
    iff.close()
    # Now do the test
    broken = test_plumed( "plumed", filename, header="", shortcutfile=name + '.json' )
    # Retrieve the html that is output by plumed
    html = get_html( inpt, name, ("master",), (broken,), ("plumed",) )
    # Remove the tempory files that we created
    if not keepfile : os.remove(filename)

    return html

def test_plumed( executible, filename, header=[], shortcutfile=[] ) :
    """
        Test if plumed can parse this input file

        This function can be used to test if PLUMED can parse an input file.  It calls plumed using subprocess

        Keyword arguments:
        executible   -- A string that contains the command for running plumed
        filename     -- A string that contains the name of the plumed input file to parse
        header       -- A string to put at the top of the error page that is output
        shortcutfile -- The file on which to output the json file containing the expansed shortcuts.  If not present this is not output 
    """
    # Get the information for running the code
    run_folder = str(pathlib.PurePosixPath(filename).parent)
    plumed_file = os.path.basename(filename)
    # Read in the plumed inpt
    nreplicas, natoms, ifile = 1, 100000, open( filename ) 
    for line in ifile.readlines() :
        if "#SETTINGS" in line :
            for word in line.split() :
                if "NREPLICAS=" in word : nreplicas = word.replace("NREPLICAS=","")
                elif "NATOMS=" in word : natoms = word.replace("NATOMS=","")
    ifile.close()
    cmd = [executible, 'driver', '--plumed', plumed_file, '--natoms', str(natoms), '--parse-only', '--kt', '2.49']
    # Add everything to ensure we can run with replicas if needs be
    if int(nreplicas)>1 : cmd = ['mpirun', '-np', str(nreplicas)] + cmd + ['--multi', str(nreplicas)]
    # Add the shortcutfile output if the user has asked for it
    if len(shortcutfile)>0 : cmd = cmd + ['--shortcut-ofile', shortcutfile]
    # raw std output - to be zipped
    outfile=filename + "." + executible + ".stdout.txt"
    # raw std error - to be zipped
    errtxtfile=filename + "." + executible + ".stderr.txt"
    # std error markdown page (with only the first 1000 lines of stderr.txt)
    errfile=filename + "." + executible + ".stderr.md"
    with open(outfile,"w") as stdout:
        with open(errtxtfile,"w") as stderr:
             with cd(run_folder):
                 plumed_out = subprocess.run(cmd, text=True, stdout=stdout, stderr=stderr )
    # write header and preamble to errfile
    with open(errfile,"w") as stderr:
        if len(header)>0 : print(header,file=stderr)
        print("Stderr for source: ",re.sub("^data/","",filename),"  ",file=stderr)
        print("Download: [zipped raw stdout](" + plumed_file + "." + executible + ".stdout.txt.zip) - [zipped raw stderr](" + plumed_file + "." + executible + ".stderr.txt.zip) ",file=stderr)
        print("{% raw %}\n<pre>",file=stderr)
        # now we print the first 1000 lines of errtxtfile to errfile
        with open(errtxtfile, "r") as stdtxterr:
          # line counter
          lc = 0
          # print comment
          print("#! Only the first 1000 rows of the error file are shown below", file=stderr)
          print("#! To inspect the full error file, please download the zipped raw stderr file above", file=stderr)
          while True:
            lc += 1
            # read line by line
            line = stdtxterr.readline()
            # if end of file or max number of lines reached, break
            if(not line or lc>1000): break
            # print line to stderr
            print(line.strip(), file=stderr)
          # close stderr
          print("</pre>\n{% endraw %}",file=stderr)
    # compress both outfile and errtxtfile
    zip(outfile)
    zip(errtxtfile)
    return plumed_out.returncode

def manage_incomplete_inputs( inpt ) :
   """
      Managet the PLUMED input files for tutorials that should contain solution

      In a tutorial you can create PLUMED input files with the instruction __FILL__
      This tells the tutees they need to add something to that input in order to make the 
      calculation work.  When you add these you should add a corrected input after the version
      with __FILL__ and after the instruction #SOLUTION.  It is this completed input that will be 
      tested

      Keyword arguments:
      inpt -- A string containing the incomplete and complete PLUMED inputs
   """
   if "__FILL__" in inpt :
       insolution, complete, incomplete = False, "", ""
       for line in inpt.splitlines() :
           if "#SOLUTION" in line : insolution=True
           elif insolution : complete += line + "\n"
           elif not insolution : incomplete += line + "\n"
       return complete, incomplete
   return inpt, ""

def get_html( inpt, name, tested, broken, plumedexe ) :
    """
       Generate the html representation of a PLUMED input file

       The html representation of a PLUMED input file has tooltips that 
       tell you what the keywords represent, a badge that shows whether the input
       works and clickable labels that provide information about the quantities that 
       are calculated.  This function uses test_plumed to check if the plumed inpt can be parsed.

       Keyword arguments:
       inpt -- A string containing the PLUMED input
       name -- The name to use for this input in the html
       tested -- The versions of plumed that were testd
       broken -- The outcome of running test plumed on the input
       plumedexe -- The plumed executibles that were used.  The first one is the one that should be used to create the input file annotations
    """
    
    # If we find the fill command then split up the input file to find the solution
    inpt, incomplete = manage_incomplete_inputs( inpt )

    # Check for include files
    foundincludedfiles, srcdir = True, str(pathlib.PurePosixPath(name).parent)
    if "INCLUDE" in inpt : foundincludedfiles, inpt = resolve_includes( srcdir, inpt, foundincludedfiles )

    # Check if there is a LOAD command in the input
    found_load = "LOAD " in inpt

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
    cmd = [plumedexe[-1], 'info', '--root']
    plumed_info = subprocess.run(cmd, capture_output=True, text=True ) 
    keyfile = plumed_info.stdout.strip() + "/json/syntax.json"
    formatfile = os.path.join(os.path.dirname(__file__),"PlumedFormatter.py")
    plumed_formatter = load_formatter_from_file(formatfile, "PlumedFormatter", keyword_file=keyfile, input_name=name, hasload=found_load, broken=broken[0] )
    plumed_file = os.path.basename(name)
    if not os.path.exists(plumed_file) : plumed_file=name

    # Now generate html of input
    html = '<div style="width: 100%; float:left">\n'
    html += '<div style="width: 90%; float:left" id="value_details_' + name + '"> Click on the labels of the actions for more information on what each action computes </div>\n'
    html += '<div style="width: 10%; float:left"><table>'
    for i in range(len(tested)) :
        btype = 'passing-green.svg'
        if broken[i] : btype = 'failed-red.svg' 
        html += '<tr><td style="padding:1px"><a href="' + plumed_file + '.' +  plumedexe[i] + '.stderr"><img src=\"https://img.shields.io/badge/' + tested[i] + '-' + btype + '" alt="tested on' + tested[i] + '" /></a></td></tr>'
    if found_load :
       html += '<tr><td style="padding:1px"><img src=\"https://img.shields.io/badge/with-LOAD-yellow.svg" alt="tested on master" /></td></tr>\n'
    if len(incomplete)>0 : 
       html += "<tr><td style=\"padding:0px\"><img src=\"https://img.shields.io/badge/" + tested[-1] + "-incomplete-yellow.svg\" alt=\"tested on " + tested[-1] + "\" onmouseup=\'toggleDisplay(\"" + name + "\")\' onmousedown=\'toggleDisplay(\"" + name + "\")\'/></td></tr>\n" 
    html += '</table></div></div>\n' 
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
       html += '</div>\n'
    else : 
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( final_inpt, plumed_lexer, plumed_formatter )

    return html
 
def resolve_includes( srcdir, inpt, foundfiles ) :
    if not foundfiles or "INCLUDE" not in inpt : return foundfiles, inpt

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

        # Now check if there is an include
        if "INCLUDE" in clines :
           # Split up the line 
           iscomment, filename = False, ""
           for w in clines.split():
               if "#" in w and filename=="" : iscomment=True
               elif "FILE=" in w : filename = w.replace("FILE=","") 
           if iscomment : 
              final_inpt += clines 
              continue
           if filename=="" : raise Exception("could not find name of file to include")
           if not os.path.exists(filename) : foundfiles = False 
           f = open( srcdir + "/" + filename, "r" )
           include_contents = f.read()
           f.close()
           final_inpt += "#SHORTCUT " + filename + "\n" + clines + "#EXPANSION " + filename + "\n# The command:\n"
           final_inpt += "# " + clines+ "# ensures PLUMED loads the contents of the file called " + filename + "\n"
           final_inpt += "# The contents of this file are shown below (click the red comment to hide them).\n" 
           foundfiles, parsed_inpt = resolve_includes( srcdir, include_contents, foundfiles )
           final_inpt += parsed_inpt + "#ENDEXPANSION " + filename + "\n"
        else : final_inpt += clines         
    return foundfiles, final_inpt


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
              final_inpt += "# as follows (Click the red comment above to revert to the short version of the input):\n" + resolve_expansions( jsondata[label]["expansion"], local_json )
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
