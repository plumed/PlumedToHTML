from PlumedToHTML import get_html
import json

# Open the json file and read it in
f = open("tests/tests.json")
tests = json.load(f)
f.close()

# Iterate through the json list
i=0
for item in tests["regtests"] :
    item["index"] = i 
    item["output"] = get_html( item["input"], "plinp" + str(i) )
    i = i + 1

# Now output the json
f = open("tests/tests.json", "w+")
f.write( json.dumps( tests, indent=3 ) )
f.close()
