#! /usr/bin/python

#
# Description: https://blog.devgenius.io/how-to-get-around-openai-gpt-3-token-limits-b11583691b32
# ================================================================
# Time-stamp: "2023-03-07 00:26:21 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import openai
import subprocess
import os, sys

openai.api_key = os.getenv('OPENAI_KEY')

# define the length of the summary (in words)
summary_length = 300

# define the length of each chunk (in tokens)
chunk_length = 1200

print(f'''\n
Number of words per summary: {summary_length}
Limit of {chunk_length} tokens per submission.
\n''')

def progressBar(value, endvalue, bar_length=50):
    '''
    progressBar(value, endvalue, bar_length=50)
                |      |         |
                |      |         --> bar_length: Length of bar to output to terminal (default = 50)
                |      --> endvalue: End of loop value - 1
                --> value: Iteration value

    ----------------------------------------------------------------------------------------------

    A simple progress bar to use in loops
    '''

    percent = float(value) / endvalue
    arrow = '=' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    if percent == 1:
        endl = '\n'
    else:
        endl = ''

    sys.stdout.write(" \r[{0}] {1}%\r{2}".format(arrow + spaces, round(percent * 100), endl))
    sys.stdout.flush()

def count_tokens(filename):
    with open(filename, 'r') as f:
        text = f.read()
    tokens = word_tokenize(text)
    return len(tokens)

def break_up_file(tokens, chunk_size, overlap_size):
    if len(tokens) <= chunk_size:
        yield tokens
    else:
        chunk = tokens[:chunk_size]
        yield chunk
        yield from break_up_file(tokens[chunk_size-overlap_size:], chunk_size, overlap_size)

def break_up_file_to_chunks(filename, chunk_size=chunk_length, overlap_size=100):
    with open(filename, 'r') as f:
        text = f.read()
    tokens = word_tokenize(text)
    return list(break_up_file(tokens, chunk_size, overlap_size))

def convert_to_detokenized_text(tokenized_text):
    prompt_text = " ".join(tokenized_text)
    prompt_text = prompt_text.replace(" 's", "'s")
    return prompt_text

def md_to_pdf(filename):
    
    filename_pdf = filename.replace('.md','.pdf')
    
    if os.path.exists("../summaries/"+filename_pdf):
        print(f"File {filename_pdf} already exists...")
        return "../summaries/"+filename_pdf
    
    cmd = f"cd ../summaries; pandoc --pdf-engine=xelatex {filename} -o {filename_pdf}"
    subprocess.check_output(cmd, shell=True).decode()

    return "../summaries/"+filename_pdf

def summarize(inp_f, item_key, collection_key, zotero):

    out_f = inp_f.replace('../text_files/','../summaries/summary_').replace('.txt','.md')
    
    if os.path.exists(out_f):
        print(f"File {out_f} already exists...\n\n")
        return out_f

    token_count = count_tokens(inp_f)
    print(f"Number of tokens: {token_count}")

    chunks = break_up_file_to_chunks(inp_f)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {len(chunk)} tokens")

    # text-davinci-003
    '''
    prompt_response = []
    for i, chunk in enumerate(chunks):
        prompt_request = "Summarize this: " + convert_to_detokenized_text(chunks[i])
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt_request,
                temperature=.5,
                max_tokens=summary_length,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
        )

        prompt_response.append(response["choices"][0]["text"].strip())
    '''

    # gpt-3.5-turbo
    prompt_response = []
    for i, chunk in enumerate(chunks):

        if len(chunks) <= 1:
            progressBar(i, len(chunks), bar_length=25)
        else:
            progressBar(i, len(chunks)-1, bar_length=25)

        prompt_request = "Summarize this scientific article: " + convert_to_detokenized_text(chunk)

        system_request = "I want you to act as a professor in the area of high to medium energy nuclear physics at Jefferson Lab. I want you to summarize content on articles in scientific detail. I want you to make sure to include dates and write out any acronyms."
        
        messages = [{"role": "system", "content": convert_to_detokenized_text(system_request)}]
        messages.append({"role": "user", "content": prompt_request})

        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=.5,
                max_tokens=summary_length,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
        )

        prompt_response.append(response["choices"][0]["message"]['content'].strip())

    prompt_request = "Consoloidate these summaries: " + str(prompt_response)

    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_request,
            temperature=.5,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

    quick_summary = response["choices"][0]["text"].strip()

    title_request = "Can you give this summary a title: " + str(prompt_response)

    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=title_request,
            temperature=.5,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

    title = response["choices"][0]["text"].strip()
    
    #template = zotero.item_template('document')
    #template['title'] = title
    #newitem = zotero.create_items([template], collection_key)
    #newitem = zotero.create_items([template])
    
    # write summary to file
    with open(out_f, "w") as f:
        f.write("#  "+title+"\n\n")
        f.write("\n## "+"Quick Summary\n\n")
        f.write("\n"+quick_summary+"\n\n")
        f.write("\n## "+"Full Summary\n\n")
        for bullet in prompt_response:
            f.write("\n* "+bullet+"\n")

    out_md = out_f.split('summaries/')[1]
        
    # convert the markdown file to PDF
    out_pdf = md_to_pdf(out_md)

    zotero.attachment_simple([out_pdf])
    
    print(f"\n\n\nFinished writing '{title}' to {out_pdf}.")

    return out_f
