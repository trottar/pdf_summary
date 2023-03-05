#! /bin/bash

#
# Description:
# ================================================================
# Time-stamp: "2023-03-05 01:59:22 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#

INPFILE=$1

echo
echo "Converting ${INPFILE}.pdf to ${INPFILE}.txt..."
echo

cp ~/Downloads/${INPFILE}.pdf text_files/

cd text_files/

pdftotext -layout ${INPFILE}.pdf ${INPFILE}.txt


echo
echo "Generating summaries for ${INPFILE}.pdf..."
echo

cd ../src/
python3.8 split_text.py ../text_files/${INPFILE}.txt
