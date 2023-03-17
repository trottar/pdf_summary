#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-03-17 14:24:59 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import sys

inp_prompt = sys.argv[1]
filename = sys.argv[2]

from pdf_to_text import pdf_to_text
from summarize_text import summarize

# Convert pdf to readable txt for gpt summary
filename_txt = pdf_to_text(filename)

# Summarize text
summarize(filename_txt, inp_prompt=inp_prompt)
