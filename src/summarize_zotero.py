#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-03-06 04:40:42 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
from pyzotero import zotero
import requests
import subprocess
import time
import os, sys

# Replace YOUR_API_KEY with your Zotero API key
api_key = os.getenv('ZOTERO_KEY')

library_id = os.getenv('ZOTERO_ID')
library_type = 'user'

from summarize_text import summarize

def pdf_to_text(filename):
    
    filename_txt = filename.replace('.pdf','.txt')
    
    if os.path.exists("../text_files/"+filename_txt):
        print(f"File {filename_txt} already exists...")
        return filename_txt
    
    cmd = f"cd ../text_files; pdftotext -layout {filename} {filename_txt}"
    subprocess.check_output(cmd, shell=True).decode()

    return filename_txt
    
zot = zotero.Zotero(library_id, library_type, api_key)
collections = zot.collections_top() # Returns a library’s top-level collections.

for collection in collections:
    if "Thesis" in collection['data']['name']:
        key = collection['data']['key']
        sub_collections = zot.collections_sub(key) # Returns the sub-collections of a specific collection
        
        for sub in sub_collections:
            sub_key = sub['data']['key']
            subsub_collections = zot.collections_sub(sub_key) # Returns the sub-collections of a specific collection

            for ss in subsub_collections:
                ss_key = ss['data']['key']
                print(f'''
[{collection['data']['name']}]-> [{sub['data']['name']}]-> [{ss['data']['name']}]
                ''')
                ss_items = zot.collection_items(ss_key) # Returns items from the specified collection. This does not include items in sub-collections

                if ss_items:
                    for item in ss_items:
                        
                        if "attachment" in item['data']['itemType']:
                            while True:
                                try:
                                    item_key = item['data']['key']
                                    url = item['data']['url']
                                    filename = item['data']['filename']

                                    if ".pdf" in filename:

                                        newfilename = "".join(filename.replace("'","").replace(".-","-").split())

                                        # Download file
                                        response = requests.get(url, stream=True)

                                        with open(os.path.expanduser("../text_files/"+newfilename), 'wb') as f:
                                            for chunk in response.iter_content(chunk_size=1024):
                                                if chunk:
                                                    f.write(chunk)

                                        print(f'\n\nDownloaded file: {newfilename}')

                                        summarize("../text_files/"+pdf_to_text(newfilename), item_key, ss_key, zot)
                                                                                
                                        break

                                    else:
                                        break
                                        
                                except subprocess.CalledProcessError as e:
                                    print(f"\n\n'{e.cmd}' failed, trying again...\n\n")
                                    print(url)
                                    time.sleep(20)
