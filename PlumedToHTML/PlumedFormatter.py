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

    def format(self, tokensource, outfile):
        action, label, all_labels, keywords, shortcut_state, shortcut_depth, default_state = "", "", [], [], 0, 0, 0
        outfile.write('<pre style="width=97%;" class="fragment">\n')
        for ttype, value in tokensource :
            # This checks if we are at the start of a new action.  If we are we should be reading a value or an action and the label and action for the previous one should be set
            if len(action)>0 and (ttype==String or ttype==Keyword) :
               if ("output" not in self.keyword_dict[action] or len(label)>0) :  
                  # This outputs information on the values computed in the previous action for the header
                  if "output" in self.keyword_dict[action] : self.writeValuesData( outfile, action, label, keywords, self.keyword_dict[action]["output"] )
                  # Reset everything for the new action
                  action, label, keywords = "", "", []
               # Check that a label has been given to actions that have output
               elif len(label)==0 and ttype==Keyword and "output" in self.keyword_dict[action] : 
                  raise Exception("action " + action + " has output but does not have label")

            if ttype==Text :
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
            elif ttype==Comment.Special :
               # This handles the mechanisms for the expandable shortcuts
               if "#NODEFAULT" in value :
                  if default_state!=0 : raise ValueError("Found rogue #NODEFAULT")
                  default_state, act_label = 1, value.replace("#NODEFAULT","").strip()
                  outfile.write('<span id="' + self.egname + "def" + act_label + '_short">')
               elif "#ENDDEFAULT" in value :
                  if default_state!=2 : raise ValueError("Found rogue #ENDDEFAULT")
                  act_label, default_state = value.replace("#ENDDEFAULT","").strip(), 0
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
                  else : shortcut_state=1
                  act_label = value.replace("#ENDEXPANSION","").strip()
                  # Now output the end of the expansion
                  outfile.write('<span style="color:blue" onclick=\'toggleDisplay("' + self.egname + act_label + '")\'>Click here to revert to the shortcut and to hide this expanded input</span></span>')
               elif "#EXPANSION" in value :
                  if shortcut_state!=1 : raise ValueError("Should only find #EXPANSION tag after #SHORTCUT tag")
                  shortcut_state = 2
                  act_label = value.replace("#EXPANSION","").strip()
                  outfile.write('</span><span id="' + self.egname + act_label + '_long" style="display:none;">')
               else : raise ValueError("Comment.Special should only catch string that are #SHORTCUT, #EXPANSION or #ENDEXPANSION")
            elif ttype==Generic:
               # whatever in KEYWORD=whatever (notice special treatment because we want to find labels so we can show paths)
               inputs, nocomma = value.split(","), True
               for inp in inputs : 
                   islab, inpt = False, inp.strip()
                   for lab in all_labels : 
                       if inpt.split('.')[0]==lab : 
                          islab=True
                          break
                   if not nocomma : outfile.write(',')
                   if islab : outfile.write('<b name="' + self.egname + inpt.split('.')[0] + '">' + inp + '</b>')
                   else : outfile.write( inp )
                   nocomma = False 
            elif ttype==String :
               # Labels of actions
               label = value.strip() 
               all_labels.append( label )
               outfile.write('<b name="' + self.egname + label + '" onclick=\'showPath("' + self.divname + '","' + self.egname + label + '")\'>' + value + '</b>')
            elif ttype==Comment :
               # Comments
               outfile.write('<span style="color:blue">' + value + '</span>' )
            elif ttype==Name.Attribute :
               # KEYWORD in KEYWORD=whatever and FLAGS
               keywords.append( value.strip() )
               outfile.write('<div class="tooltip">' + value + '<div class="right">' + self.keyword_dict[action][value.strip()].split('.')[0] + '<i></i></div></div>')
            elif ttype==Name.Constant :
               # @replicas in special replica syntax
               outfile.write('<div class="tooltip">' + value + '<div class="right">This keyword specifies that different replicas have different values for this quantity.  See <a href="' + self.keyword_dict["replicalink"] +'">here for more details.</a><i></i></div></div>')
            elif ttype==Keyword :
               # Name of action
               action = value.strip()
               if shortcut_state==1 and default_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right"><a href="' + self.keyword_dict[action]["hyperlink"] + '">open documentation</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\' >show defaults</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>expand shortcut</a><i></i></div></div> ')
               elif shortcut_state==1 and default_state==2 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right"><a href="' + self.keyword_dict[action]["hyperlink"] + '">open documentation</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\' >hide defaults</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>expand shortcut</a><i></i></div></div> ')
               elif default_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right"><a href="' + self.keyword_dict[action]["hyperlink"] + '">open documentation</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\' >show defaults</a><i></i></div></div> ')
               elif default_state==2 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right"><a href="' + self.keyword_dict[action]["hyperlink"] + '">open documentation</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + "def" + label + '");\' >hide defaults</a><i></i></div></div> ')
               elif shortcut_state==1 :
                    outfile.write('<div class="tooltip" style="color:green">' + value.strip() + '<div class="right">This is a shortcut so you can:</br><a href="' + self.keyword_dict[action]["hyperlink"] + '">open documentation</a></br><a href=\'javascript:;\' onclick=\'toggleDisplay("' + self.egname + label + '");\'>expand shortcut</a><i></i></div></div> ')
               else : outfile.write('<a href="' + self.keyword_dict[action]["hyperlink"] + '" style="color:green">' + value.strip() + '</a> ')
          
        # Check if there is stuff to output for the last action in the file
        if action in self.keyword_dict and "output" in self.keyword_dict[action] :
           if len(label)==0 : raise Exception("action " + action + " has output but does not have label") 
           self.writeValuesData( outfile, action, label, keywords, self.keyword_dict[action]["output"] )
        outfile.write('</pre></div>')

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
 
