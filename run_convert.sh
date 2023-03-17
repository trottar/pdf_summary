#! /bin/bash

#
# Description:
# ================================================================
# Time-stamp: "2023-03-17 14:22:34 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#

# Flag definitions (flags: h, f)
while getopts 'hf' flag; do
    case "${flag}" in
        h) 
        echo "--------------------------------------------------------------"
        echo "./run_convert.sh -{flags} {variable arguments, see help}"
	echo
        echo "Description: Summarize pdf. If no flag given, grabs files from zotero"
        echo "--------------------------------------------------------------"
        echo
        echo "The following flags can be called for the heep analysis..."
        echo "    -h, help"
        echo "    -f, Run for specific file"
	echo "        PROMPT=arg1, FILENAME=arg2"
        exit 0
        ;;
        f) f_flag='true' ;;
        *) print_usage
        exit 1 ;;
    esac
done


if [[ $f_flag = "true" ]]; then

    PROMPT=$2
    FILENAME=$3

    echo
    echo "Generating summaries for ${FILENAME}..."
    echo

    cd src/
    python3.8 general_summary.py $PROMPT $FILENAME
    
    
else

    INPFILE=$1

    echo
    echo "Generating summaries..."
    echo

    cd src/
    python3.8 summarize_zotero.py

    cd ../text_files/
    rm -f *.pdf
    rm -f *.txt
    
fi
