#! /bin/bash

#
# Description:
# ================================================================
# Time-stamp: "2023-03-06 00:37:55 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#

INPFILE=$1

echo
echo "Generating summaries..."
echo

cd src/
python3.8 summarize_zotero.py

cd ../text_files/
rm -f *.pdf
rm -f *.txt
