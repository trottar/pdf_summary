#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-03-06 19:47:38 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import glob
import openai
import pandas as pd
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import os, sys

openai.api_key = os.getenv('OPENAI_KEY')

# maximum number of tokens per submission
max_tokens = 2000

# define the length of each chunk (in tokens)
chunk_length = 1500

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

def combine_md():

    # Set the path to the directory containing the markdown files
    md_dir_path = "../summaries/"

    # Set the name of the output text file
    txt_file_name = "combined_text_file.txt"

    # Create a list of all the markdown files in the directory
    md_file_paths = glob.glob(md_dir_path + "*.md")

    # Open the output text file for writing
    with open(txt_file_name, "w") as txt_file:
        # Loop over each markdown file
        for md_file_path in md_file_paths:
            # Open the markdown file for reading
            with open(md_file_path, "r") as md_file:
                # Read the contents of the markdown file
                md_file_contents = md_file.read()
                # Write the contents of the markdown file to the output text file
                txt_file.write(md_file_contents)
                # Add a newline character to separate the contents of each file
                txt_file.write("\n")

    # Print a message to indicate that the process is complete
    print("Combined all markdown files into one text file.")

    return txt_file_name

def chat(messages):
        # gpt-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=.5,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        api_usage = response['usage']
        print(f"\n\nTotal tokens comsumed: {api_usage}\n\n")

        messages.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    
        return messages

inp_f = combine_md()

token_count = count_tokens(inp_f)
print(f"Number of tokens: {token_count}")

chunks = break_up_file_to_chunks(inp_f)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {len(chunk)} tokens")

#prompt_request = '''
#I want you to act as a professor in the area of high to medium energy nuclear physics. I will first provide {len(chunks)} summaries of articles that I want you to remember. After you recieve {len(chunks)} summaries, I will provide some topics related to the study of high to medium energy nuclear physics, and it will be your job to explain these concepts in an easy-to-understand manner. I will also provide some questions, ending with a question mark, that will require specific knowledge of Hall C at Jefferson Lab. This could include providing examples, posing questions or breaking down complex ideas into smaller pieces that are easier to comprehend. You may use the summaries I provide as further sources of information.
#'''

prompt_request = '''
I want you to act as a professor in the area of high to medium energy nuclear physics. I will provide some topics related to the study of high to medium energy nuclear physics, and it will be your job to explain these concepts in an easy-to-understand manner. I will also provide some questions, ending with a question mark, that will require specific knowledge of Hall C at Jefferson Lab. This could include providing examples, posing questions or breaking down complex ideas into smaller pieces that are easier to comprehend.
'''

messages = []
messages.append({"role": "system", "content": convert_to_detokenized_text(prompt_request)})
messages = chat(messages)
print('{0}: {1}\n'.format(messages[-1]['role'].strip(), messages[-1]['content'].strip()))

'''
for i, chunk in enumerate(chunks):

    if len(chunks) <= 1:
        progressBar(i, len(chunks), bar_length=25)
    else:
        progressBar(i, len(chunks)-1, bar_length=25)
        
    prompt_request = f"Summary {i+1}/{len(chunks)}: {chunk}"

    messages.append({"role": "user", "content": convert_to_detokenized_text(prompt_request)})
    messages = chat(messages)
    #print('{0}: {1}\n'.format(messages[-1]['role'].strip(), messages[-1]['content'].strip()))

messages.append({"role": "user", "content": "End of summaries!"})
messages = chat(messages)
'''
    
# Loop through the conversation
while True:
            
    user_inp =  input('Please enter your prompt...')

    if "bye" in user_inp:
        break

    prompt_request = f"My first request is '{user_inp}'"
    
    messages.append({"role": "user", "content": convert_to_detokenized_text(prompt_request)})
    messages = chat(messages)
    print('{0}: {1}\n'.format(messages[-1]['role'].strip(), messages[-1]['content'].strip()))
