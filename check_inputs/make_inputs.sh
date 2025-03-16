#!/bin/bash
# if PlumedToHTMLInstalled is not exported, assume it is not installed
PlumedToHTMLInstalled=${PlumedToHTMLInstalled:-no}
# This script will test PlumedToHTML (without needing to install it)

# Clean the previous run
rm -rf testDir
mkdir testDir
cd testDir || {
    echo "error in creating the testDirectory"
    exit 1
}
if [[ $PlumedToHTMLInstalled = no ]]; then
    # Create symbolic links to PlumedToHTML
    ln -s ../../src/PlumedToHTML/PlumedFormatter.py .
    ln -s ../../src/PlumedToHTML/PlumedToHTML.py .
    ln -s ../../src/PlumedToHTML/PlumedLexer.py .
    ln -s ../../src/PlumedToHTML/PlumedCLtoolLexer.py
    ln -s ../../src/PlumedToHTML/PlumedCLFileLexer.py .
    ln -s ../../src/PlumedToHTML/assets .
fi
ln -s ../../tdata .
cp ../create_inputs.py .
# And run the python script
python create_inputs.py >check_site.html
