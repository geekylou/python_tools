import sys
import json
import sys


def create_chapters(metadata):
    offset = 0
    last_part_id = 0
    offsets = {}
    output = ""
    # Assume parts are in order.
    for part in metadata["Spine"]:
        offsets[part['Id']] = {'offset': offset}
        offset = offset + part['Duration']
        last_part_id = part['Id']
        #print part['Duration'],part['Id']
    offsets[last_part_id+1] = {'offset': offset}

    output = output + ";FFMETADATA1\n"

    for chapter in metadata['Navigation']:
        #print chapter, " Full offset:", chapter['Offset'] + offsets[chapter['PartId']]['offset']
        
        output = output + "[CHAPTER]\n"
        output = output + "TIMEBASE=1/1000000000\n"
        output = output + "START="+str(int((chapter['Offset'] + offsets[chapter['PartId']]['offset']) * 1000000000.0)) + "\n"
        output = output + "END="+str(int((chapter['Offset'] + offsets[chapter['PartId']+1]['offset']) * 1000000000.0)) + "\n"
        output = output + "title="+chapter['Title'] + "\n"
    return output
def create_filelist(metadata):
    #print(metadata["Spine"])
    # Assume parts are in order.
    for part in metadata["Spine"]:
        #print(part['Duration'],part['Id'])
        print("file '"+str(part['Id']+1)+".mp3'")
        #print("file '"+part['filePath'].split('/')[-1]+"'")

metadata = json.loads(sys.stdin.read())
        
if sys.argv[1] == 'filelist':
    create_filelist(metadata)
elif sys.argv[1] == 'chapters':
    print(create_chapters(metadata))