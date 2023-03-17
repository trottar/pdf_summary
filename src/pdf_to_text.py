#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-03-17 14:25:20 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import subprocess
import os

def pdf_to_text(filename):
    
    filename_txt = filename.replace('.pdf','.txt')
    
    if os.path.exists("../text_files/"+filename_txt):
        print(f"File {filename_txt} already exists...")
        return filename_txt
    
    cmd = f"cd ../text_files; pdftotext -layout {filename} {filename_txt}"
    subprocess.check_output(cmd, shell=True).decode()

    return filename_txt
