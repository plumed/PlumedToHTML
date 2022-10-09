from pygments.formatter import Formatter
from pygments.token import Text, Comment, Literal, Keyword, Name, Generic, String
import json

class PlumedFormatter(Formatter):
    def __init__(self, **options) :
        Formatter.__init__(self, **options) 
        # Retrieve the dictionary of keywords from the json
        with open(options["keyword_file"]) as f : self.keyword_dict = json.load(f)
        self.divname=options["input_name"]
        self.egname=options["input_name"]
        self.hasload=options["hasload"]
        self.broken=options["broken"]

    def format(self, tokensource, outfile):
        action, label, all_labels, keywords, shortcut_state, shortcut_depth, default_state, notooltips, expansion_label = "", "", [], [], 0, 0, 0, False, ""
        outfile.write('<pre style="width=97%;">\n')
        for ttype, value in tokensource :
            # This checks if we are at the start of a new action.  If we are we should be reading a value or an action and the label and action for the previous one should be set
            if len(action)>0 and (ttype==String or ttype==Keyword or ttype==Comment.Preproc) :
               if notooltips : 
                  # Reset everything for the new action
                  action, label, keywords, notooltips = "", "", [], False
               else :
                  # This outputs information on the values computed in the previous action for the header
                  if "output" in self.keyword_dict[action]["syntax"] : self.writeValuesData( outfile, action, label, keywords, self.keyword_dict[action]["syntax"]["output"] )
                  # Reset everything for the new action
                  action, label, keywords = "", "", []

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
               outfile.write('<span style="color:red" onclick=\'toggleDisplay("' + self.egname + expansion_label + '")\'>' + value + '</span>')
            elif ttype==Comment.Special or ttype==Comment.Preproc :
               # This handles the mechanisms for the expandable shortcuts
               act_label=""
               if "#NODEFAULT" in value :
                  if default_state!=0 : raise ValueError("Found rogue #NODEFAULT")
                  default_state, act_label = 1, value.replace("#NODEFAULT","").strip()
                  outfile.write('<span id="' + self.egname + "def" + act_label + '_short">')
               elif "#ENDDEFAULT" in value :
                  if default_state!=2 : raise ValueError("Found rogue #ENDDEFAULT")
                  default_state = 0
                  outfile.write('</span>')
               elif "#DEFAULT" in value :
                  if default_state!=1 : raise ValueError("Found rogue #DEFAULT")
                  act_label, default_state = value.replace("#DEFAULT","").strip(), 2
                  outfile.write('</span><span id="' + self.egname + "def" + act_label + '_long" style="display:none;">')
               elif "#SHORTCUT" in value :
                  if shortcut_depth==0 and shortcut_state!=0 : raise ValueError("Found rogue #SHORTCUT")
                  shortcut_state, shortcut_depth = 1, shortcut_depth + 1
                  act_label = value.replace("#SHORTCUT","").strip()
                  outfile.write('<span id="' + self.egname + act_label + '_short">')
               elif "#ENDEXPANSION" in value :
                  if shortcut_state!=2 : raise ValueError("Should only find #ENDEXPANSION tag after #EXPANSION tag")
                  shortcut_depth = shortcut_depth - 1
                  if shortcut_depth==0 : shortcut_state=0
                  act_label = value.replace("#ENDEXPANSION","").strip()
                  # Now output the end of the expansion
                  outfile.write('<span style="color:blue"># --- End of included input --- </span></span>')
               elif "#EXPANSION" in value :
                  if shortcut_state!=1 : raise ValueError("Should only find #EXPANSION tag after #SHORTCUT tag")
                  shortcut_state = 2
                  act_label, expansion_label = value.replace("#EXPANSION","").strip(), value.replace("#EXPANSION","").strip()
                  outfile.write('</span><span id="' + self.egname + act_label + '_long" style="display:none;">')
               else : raise ValueError("Comment.Special should only catch string that are #SHORTCUT, #EXPANSION or #ENDEXPANSION")
               # This sets up the label at the start of a new block with NODEFAULT or SHORTCUT
               if ttype==Comment.Preproc :
                  if label!="" and label!=act_label : raise Exception("label for shortcut (" + act_label + ") doesn't match action label (" + label + ")")
                  elif label=="" : label = act_label 
            elif ttype==Generic:
               # whatever in KEYWORD=whatever 
               if action=="INCLUDE" and shortcut_state==1 : 
                  # special treatment for filename in INCLUDE FILE=filename
                  outfile.write('<a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>' + value + '</a>') 
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
                      else : outfile.write( inp )
                      nocomma = False 
            elif ttype==String or ttype==String.Double :
               # Labels of actions
               if not self.broken and action!="" and label!="" and label!=value.strip() : raise Exception("label for " + action + " is not what is expected.  Is " + label + " should be " + value.strip() )
               elif label=="" : label = value.strip() 
               all_labels.append( label )
               outfile.write('<b name="' + self.egname + label + '" onclick=\'showPath("' + self.divname + '","' + self.egname + label + '")\'>' + value + '</b>')
            elif ttype==Comment :
               # Comments
               outfile.write('<span style="color:blue">' + value + '</span>' )
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
                     if not self.broken and not notooltips and not foundkey : raise Exception("keyword " + value.strip().upper() + " is not in syntax for action " + action )
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
               if notooltips :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">This action is not part of PLUMED and was included by using a LOAD command <a href="' + self.keyword_dict["LOAD"]["hyperlink"] + '" style="color:green">More details</a><i></i></div></div>') 
               elif shortcut_state==1 and default_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action is <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>a shortcut</a> and it has <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\'>hidden defaults</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>') 
               elif shortcut_state==1 and default_state==2 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action is <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>a shortcut</a> and uses the <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\'>defaults shown here</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               elif default_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action has <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\'>hidden defaults</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               elif default_state==2 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action uses the <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\'>defaults shown here</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               elif shortcut_state==1 :
                    if action=="INCLUDE" : outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a>. Show <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>included file</a><i></i></div></div>')
                    else : outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">' + self.keyword_dict[action]["description"] + ' This action is <a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>a shortcut</a>. <a href="' + self.keyword_dict[action]["hyperlink"] + '">More details</a><i></i></div></div>')
               else :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">'+ self.keyword_dict[action]["description"] + ' <a href="' + self.keyword_dict[action]["hyperlink"] + '" style="color:green">More details</a><i></i></div></div>')
        # Check if there is stuff to output for the last action in the file
        if action in self.keyword_dict and "output" in self.keyword_dict[action]["syntax"] and len(label)>0 :
           self.writeValuesData( outfile, action, label, keywords, self.keyword_dict[action]["syntax"]["output"] )
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
 
