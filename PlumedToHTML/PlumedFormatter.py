from pygments.formatter import Formatter
from pygments.token import Text, Comment, Literal, Keyword, Name, Generic, String
from requests.exceptions import InvalidJSONError
import html
import json

class PlumedFormatter(Formatter):
    def __init__(self, **options) :
        Formatter.__init__(self, **options) 
        # Retrieve the dictionary of keywords from the json
        with open(options["keyword_file"]) as f :
           try:
              self.keyword_dict = json.load(f)
           except ValueError as ve:
              raise InvalidJSONError(ve) 
        self.divname=options["input_name"]
        self.egname=options["input_name"]
        self.hasload=options["hasload"]
        self.broken=options["broken"]
        self.valuedict=options["valuedict"]
        self.actions=options["actions"]
        self.valcolors = { 
           "scalar": "black", 
           "atoms": "violet", 
           "vector": "blue", 
           "matrix": "red", 
           "grid": "green", 
           "mix": "brown" 
        }

    def format(self, tokensource, outfile):
        action, label, all_labels, keywords, shortcut_state, shortcut_depth, default_state, notooltips, expansion_label, hidden_state, hidenum = "", "", set(), [], 0, 0, 0, False, "", 0, 0
        outfile.write('<pre style="width=97%;">\n')
        for ttype, value in tokensource :
            # This checks if we are at the start of a new action.  If we are we should be reading a value or an action and the label and action for the previous one should be set
            if len(action)>0 and (ttype==String or ttype==Keyword or ttype==Comment.Preproc) :
               if notooltips : 
                  # Reset everything for the new action
                  action, label, keywords, notooltips = "", "", [], False
               else :
                  # This outputs information on the values computed in the previous action for the header
                  if label not in self.valuedict.keys() and label not in all_labels : 
                     all_labels.add(label)
                     if action in self.keyword_dict and "output" in self.keyword_dict[action]["syntax"] : self.writeValuesData( outfile, action, label, keywords, self.keyword_dict[action]["syntax"]["output"] )
                     else : 
                        outfile.write('<span style="display:none;" id="' + self.egname + label + r'">')
                        outfile.write('The ' + action + ' action with label <b>' + label + '</b> calculates something') 
                        outfile.write('</span>') 
                  # Reset everything for the new action
                  action, label, keywords = "", "", []

            # Check users inputs for rogue # symbols that have been lexed into the wrong place
            if "#" in value and ttype!=Comment and ttype!=Comment.Hashbang and ttype!=Comment.Special and ttype!=Comment.Preproc and ttype!=Literal : 
                raise ValueError("found # in {" + value + "} but this string has not been identified as a comment by the lexer.  If you have colons in your comments they are known to cause this error.  If you remove the colons from the comments the input may parse.")

            if ttype==Text.Whitespace :
               # Blank lines
               outfile.write( '<br/>' )
            elif ttype==Text :
               # Non PLUMED stuff
               outfile.write( value )
            elif ttype==Literal :
               # __FILL__ for incomplete values
               if( value=="__FILL__" ) : 
                   outfile.write('<span style="background-color:yellow">__FILL__</span>')
               # This is for vim syntax expression
               elif "vim:" in value :
                   outfile.write('<div class="tooltip" style="color:blue">' + value + '<div class="right">Enables syntax highlighting for PLUMED files in vim. See <a href="' + self.keyword_dict["vimlink"] + '">here for more details. </a><i></i></div></div>')
               else : raise ValueError("found invalid Literal in input " + value)
            elif ttype==Comment.Hashbang :
               # This handles the mechanism for closing the expanding shortcut
               if shortcut_state!=2 : raise ValueError("Should only find line to close shortcut between #EXPANSION and #ENDEXPANSION tags")
               outfile.write('<span class="toggler" style="color:red" onclick=\'toggleDisplay("' + self.egname + expansion_label + '")\'>' + value + '</span>')
            elif ttype==Comment.Special or ttype==Comment.Preproc :
               # This handles the mechanisms for the expandable shortcuts
               act_label=""
               if "#NODEFAULT" in value :
                  if default_state!=0 : raise ValueError("Found rogue #NODEFAULT")
                  default_state, act_label = 1, html.escape( value.replace("#NODEFAULT","").strip() )
                  outfile.write('<span id="' + self.egname + "def" + act_label + '_short">')
               elif "#ENDDEFAULT" in value :
                  if default_state!=2 : raise ValueError("Found rogue #ENDDEFAULT")
                  default_state = 0
                  outfile.write('</span>')
               elif "#DEFAULT" in value :
                  if default_state!=1 : raise ValueError("Found rogue #DEFAULT")
                  act_label, default_state = html.escape( value.replace("#DEFAULT","").strip() ), 2
                  outfile.write('</span><span id="' + self.egname + "def" + act_label + '_long" style="display:none;">')
               elif "#SHORTCUT" in value :
                  if shortcut_depth==0 and shortcut_state!=0 : raise ValueError("Found rogue #SHORTCUT")
                  shortcut_state, shortcut_depth = 1, shortcut_depth + 1
                  act_label = html.escape( value.replace("#SHORTCUT","").strip() )
                  outfile.write('<span id="' + self.egname + act_label + '_short">')
               elif "#ENDEXPANSION" in value :
                  if shortcut_state!=2 : raise ValueError("Should only find #ENDEXPANSION tag after #EXPANSION tag")
                  shortcut_depth = shortcut_depth - 1
                  if shortcut_depth==0 : shortcut_state=0
                  act_label = html.escape( value.replace("#ENDEXPANSION","").strip() )
                  # Now output the end of the expansion
                  outfile.write('<span style="color:blue"># --- End of included input --- </span></span>')
               elif "#EXPANSION" in value :
                  if shortcut_state!=1 : raise ValueError("Should only find #EXPANSION tag after #SHORTCUT tag")
                  shortcut_state = 2
                  act_label, expansion_label = html.escape( value.replace("#EXPANSION","").strip() ), value.replace("#EXPANSION","").strip()
                  outfile.write('</span><span id="' + self.egname + act_label + '_long" style="display:none;">')
               elif "#ENDHIDDEN" in value :
                  if hidden_state != 1 : raise ValueError("Found rogue #ENDHIDDEN")
                  hidden_state = 0 
                  outfile.write('<a class="toggler" style="color:red" onclick=\'toggleDisplay("' + self.egname + "_hiddenpart" + str(hidenum) + '")\'># --- Click here to hide input --- \n</a></span>')
               elif "#HIDDEN" in value :
                  if hidden_state != 0 : raise ValueError("Found rogue #HIDDEN in already hidden input") 
                  hidden_state, hidenum = 1, hidenum + 1
                  outfile.write('<span id="' + self.egname + "_hiddenpart" + str(hidenum) + '_short">')
                  outfile.write('<a class="toggler" style="color:red" onclick=\'toggleDisplay("' + self.egname + "_hiddenpart" + str(hidenum) + '")\'># --- Click here to reveal hidden parts of input file ---- \n</a></span>')
                  outfile.write('<span id="' + self.egname + "_hiddenpart" + str(hidenum) + '_long" style="display:none;">')
               else : raise ValueError("Found " + value.strip() + " in Comment.Special should only catch string that are #SHORTCUT, #EXPANSION, #ENDEXPANSION, #HIDDEN or #ENDHIDDEN")
               # This sets up the label at the start of a new block with NODEFAULT or SHORTCUT
               if ttype==Comment.Preproc :
                  if label!="" and label!=act_label : raise Exception("label for shortcut (" + act_label + ") doesn't match action label (" + label + ")")
                  elif label=="" : label = act_label 
            elif ttype==Generic:
               # whatever in KEYWORD=whatever 
               if action=="INCLUDE" and shortcut_state==1 : 
                  # special treatment for filename in INCLUDE FILE=filename
                  outfile.write('<a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>' + value + '</a>') 
               else :
                  # notice special treatment here because we want to find labels so we can show paths
                  inputs, nocomma = value.split(","), True
                  for inp in inputs : 
                      islab, inpt = False, inp.strip()
                      for lab in all_labels : 
                          if inpt.split('.')[0]==lab : 
                             islab=True
                             break
                      if not nocomma : outfile.write(',')
                      if islab : outfile.write('<b name="' + self.egname + inpt.split('.')[0] + '">' + inp + '</b>')
                      # Deal with atom selections
                      elif "@" in inp :
                        # Deal with residue
                        if "-" in inp : 
                            select, defs, residue = "", inp.split("-"), "" 
                            if "_" in defs[1] : 
                                resp = defs[1].split("_")
                                residue = "residue " + resp[1] + " in chain " + resp[0]
                            else : residue = "residue " + defs[1]  
                            select = defs[0] + "-"
                            if select not in self.keyword_dict["groups"] : tooltip, link = "the " + defs[0][1:] + " atom in " + residue, self.keyword_dict["groups"]["@protein"]["link"]
                            else : tooltip, link = self.keyword_dict["groups"][select]["description"] + " " + residue, self.keyword_dict["groups"][select]["link"]
                        else : 
                            select = inp.strip()
                            if select not in self.keyword_dict["groups"] : raise Exception("special group " + select + " not in special group dictionary")
                            tooltip, link = self.keyword_dict["groups"][select]["description"], self.keyword_dict["groups"][select]["link"]
                        outfile.write('<div class="tooltip">' + inp + '<div class="right">' + tooltip + '. <a href="' + link + '">Click here</a> for more information. <i></i></div></div>') 
                      else : outfile.write( html.escape(inp) )
                      nocomma = False 
            elif ttype==String or ttype==String.Double :
               # Labels of actions
               if not self.broken and action!="" and label!="" and label!=value.strip() : raise Exception("label for " + action + " is not what is expected.  Is " + label + " should be " + value.strip() )
               elif label=="" : label = html.escape( value.strip() ) 
               valtype = "mix"
               if label in self.valuedict.keys() :
                  valtype = "unset"
                  for key, ddd in self.valuedict[label].items() :
                      if key=="action" : continue
                      elif valtype=="unset" : valtype = ddd["type"]
                      elif valtype!=ddd["type"] : valtype = "mix" 
               if shortcut_state==1 and "shortcut_" + label in self.valuedict.keys() : 
                  outfile.write('<b name="' + self.egname + label + '" onclick=\'showPath("' + self.divname + '","' + self.egname + label + '","' + self.egname + label + '_shortcut","' + self.valcolors[valtype] + '")\'>' + value + '</b>') 
                  if label + "_shortcut" not in all_labels :
                     all_labels.add(label + "_shortcut") 
                     self.writeValueInfo( outfile, label, label + "_shortcut", self.valuedict["shortcut_" + label] )
               else : 
                  outfile.write('<b name="' + self.egname + label + '" onclick=\'showPath("' + self.divname + '","' + self.egname + label + '","' + self.egname + label + '","' + self.valcolors[valtype] + '")\'>' + value + '</b>')
                  if label in self.valuedict.keys() and label not in all_labels :
                     all_labels.add(label)
                     self.writeValueInfo( outfile, label, label, self.valuedict[label] )
            elif ttype==Comment :
               # Comments
               outfile.write('<span style="color:blue" class="comment">' + html.escape(value) + '</span>' )
            elif ttype==Name.Attribute :
               # KEYWORD in KEYWORD=whatever and FLAGS
               keywords.append( value.strip().upper() )
               if notooltips :
                  outfile.write( value.strip() )
               else :
                  desc = ""
                  if value.strip().upper() in self.keyword_dict[action]["syntax"] : desc = self.keyword_dict[action]["syntax"][value.strip().upper()]["description"].split('.')[0]
                  else :
                     # This deals with numbered keywords
                     foundkey=False
                     for kkkk in self.keyword_dict[action]["syntax"] :
                         if kkkk=="output" or self.keyword_dict[action]["syntax"][kkkk]["multiple"]==0 : continue
                         if kkkk in value.strip() : foundkey, desc = True, self.keyword_dict[action]["syntax"][kkkk.upper()]["description"].split('.')[0]
                     if not self.broken and not notooltips and not foundkey : 
                        if self.hasload : foundkey, desc = True, 'There is a possibity that this action is not part of PLUMED and was included by using a LOAD command. This LOADing replaces one of the actions that is in PLUMED. You should thus be wary of the documentation in these tooltips and look at the cpp file that was loaded <a href="' + self.keyword_dict["LOAD"]["hyperlink"] + '" style="color:green">More details</a>'
                        else : raise Exception("keyword " + value.strip().upper() + " is not in syntax for action " + action )
                  if desc=="" and self.broken : outfile.write( value )
                  else : outfile.write('<div class="tooltip">' + value + '<div class="right">' + desc + '<i></i></div></div>')
            elif ttype==Name.Constant :
               # @replicas in special replica syntax
               if value=="@replicas:" : 
                  outfile.write('<div class="tooltip">' + value + '<div class="right">This keyword specifies that different replicas have different values for this quantity.  See <a href="' + self.keyword_dict["replicalink"] +'">here for more details.</a><i></i></div></div>')
               # Deal with external libraries doing atom selections
               else :
                  if value not in self.keyword_dict["groups"] : raise Exception("special group " + value + " not in special group dictionary")
                  outfile.write('<div class="tooltip">' + value + '<div class="right">' + self.keyword_dict["groups"][value]["description"] + '.  <a href="' + self.keyword_dict["groups"][value]["link"] + '">Click here</a> for more information. <i></i></div></div>');
            elif ttype==Keyword :
               # Name of action
               action, notooltips = value.strip().upper(), False
               if action not in self.keyword_dict : 
                  if self.hasload or self.broken : notooltips = True
                  else : raise Exception("no action " + action + " in dictionary")
               else :
                  # Store name of action in set that contains all action names
                  self.actions.add(action)
               if default_state!=0 or shortcut_state==1 : 
                  if label!="" and label!=act_label : raise Exception("mismatched label and act_label for shortcut/default") 
               if notooltips :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">This action is not part of PLUMED and was included by using a LOAD command <a href="' + self.keyword_dict["LOAD"]["hyperlink"] + '" style="color:green">More details</a><i></i></div></div>') 
               elif shortcut_state==1 and default_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action is <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>a shortcut</a> and it has <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + act_label + '");\'>hidden defaults</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>') 
               elif shortcut_state==1 and default_state==2 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action is <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + act_label + '");\'>a shortcut</a> and uses the <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + act_label + '");\'>defaults shown here</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               elif default_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action has <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + act_label + '");\'>hidden defaults</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               elif default_state==2 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action uses the <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + act_label + '");\'>defaults shown here</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               elif shortcut_state==1 :
                    if action=="INCLUDE" : outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a>. Show <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + act_label + '");\'>included file</a><i></i></div></div>')
                    else : outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action is <a class="toggler" href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + act_label + '");\'>a shortcut</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               else :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">'+ self.keyword_dict[action]["description"] + ' <a href="' + self.keyword_dict[action]["hyperlink"] + '" style="color:green">More details</a><i></i></div></div>')
        # Check if there is stuff to output for the last action in the file
        if len(label)>0 and label not in all_labels and label not in self.valuedict.keys() :
           all_labels.add( label )
           if action in self.keyword_dict and "output" in self.keyword_dict[action]["syntax"] : self.writeValuesData( outfile, action, label, keywords, self.keyword_dict[action]["syntax"]["output"] )
           else : 
              outfile.write('<span style="display:none;" id="' + self.egname + label + r'">')
              outfile.write('The ' + action + ' action with label <b>' + label + '</b> calculates something')
              outfile.write('</span>')
        outfile.write('</pre>')

    def writeValuesData( self, outfile, action, label, keywords, outdict ) :
        # Some header stuff 
        outfile.write('<span style="display:none;" id="' + self.egname + label + r'">')
        outfile.write('The ' + action + ' action with label <b>' + label + '</b>')
        # Check for components
        found_flags = False
        for key, value in outdict.items() :
            for flag in keywords :
                if flag==value["flag"] or value["flag"]=="default" : found_flags=True
        # Output string for value
        if not found_flags and "value" in outdict : 
            outfile.write(' calculates ' + outdict["value"]["description"] )
        # Output table containing descriptions of all components
        else :
            outfile.write(' calculates the following quantities:')
            outfile.write('<table  align="center" frame="void" width="95%" cellpadding="5%">')
            outfile.write('<tr><td width="5%"><b> Quantity </b>  </td><td><b> Description </b> </td></tr>')    
            for key, value in outdict.items() :
                present = False 
                for flag in keywords : 
                    if flag==value["flag"] : present=True
                if present or value["flag"]=="default" : outfile.write('<tr><td width="5%">' + label + "." + key + '</td><td>' + value["description"] + '</td></tr>')
            outfile.write('</table>')
        outfile.write('</span>')

    def writeValueInfo( self, outfile, label, span_label, valinfo ) :
        # Some header stuff 
        outfile.write('<span style="display:none;" id="' + self.egname + span_label + r'">')
        outfile.write('The ' + valinfo["action"] + ' action with label <b>' + label + '</b>')
        outfile.write(' calculates the following quantities:')
        outfile.write('<table  align="center" frame="void" width="95%" cellpadding="5%">')
        outfile.write('<tr><td width="5%"><b> Quantity </b>  </td><td width="5%"><b> Type </b>  </td><td><b> Description </b> </td></tr>')
        for key, value in valinfo.items() :
            if key=="action" : continue
            outfile.write('<tr><td width="5%">' + key + '</td><td width="5%"><font color="' + self.valcolors[value["type"]] +'">' + value["type"] + '</font></td><td>' + value["description"] + '</td></tr>')
        outfile.write('</table>') 
        outfile.write('</span>')
 
