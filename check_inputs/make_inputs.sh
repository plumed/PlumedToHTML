#!/bin/bash

# Delete all the crap from the last time we ran this
for file in `ls .` ; do
    if [ $file != "make_inputs.sh" ] && [ $file != "create_inputs.py" ] ; then 
       rm -rf $file
    fi
done

# Create symbolic links to PlumedToHMTL
ln -s ../PlumedToHTML/PlumedFormatter.py .
ln -s ../PlumedToHTML/PlumedToHTML.py .
ln -s ../PlumedToHTML/PlumedLexer.py
ln -s ../PlumedtoHTML/assets .
ln -s ../tdata .

# And run the python
python create_inputs.py > check_site.html
