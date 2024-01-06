#!/bin/bash

#
# Add the following below data = response.json() in __DownloadAudiobook in kobo.py in the kobodl python package:
#   with open(outputPath+"/metadata.json", "w") as f:
#     f.write(json.dumps(data))
#     f.close()
# This will create a metadata.json file that can be used with the scripts below to create a mkv or mp4 file (encoded with mp3) with chapter information.
#

python ~/create_audiobook_metadata.py <matadata.json filelist >filelist.txt
python ~/create_audiobook_metadata.py <matadata.json chapters >chapters.txt

ffmpeg -i chapters.txt -f concat -safe 1 -i filelist.txt -map_metadata 0 -codec copy out.mkv
ffmpeg -i out.mkv -acodec copy out_mp3.mp4