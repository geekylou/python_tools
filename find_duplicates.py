import sys
import argparse

parser = argparse.ArgumentParser(description='Check base against backups')
parser.add_argument('base_filename')  
parser.add_argument('check_filename')
parser.add_argument('--file-list',action='store_true')
args = parser.parse_args()

hashes = {}

with open(args.base_filename,'r') as f:
  for line in f:
    hash_pos = line.find(' ')
    hash = line[:hash_pos].strip()
    filename = line[hash_pos+1:].strip()

#    filename = filename[filename.find('/')+1:]

    if filename not in hashes:
        hashes[hash] = filename
#    print(hash,',',filename)

    
with open(args.check_filename,'r') as f:
  for line in f:
    hash_pos = line.find(' ')
    hash = line[:hash_pos].strip()
    filename = line[hash_pos+1:].strip()

    if hash in hashes:
        if args.file_list:
            print('"'+filename+'"')
        else:
            print("Duplicate",filename,hashes[hash])
