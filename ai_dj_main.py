#import generateText
from mutagen.easyid3 import EasyID3 #mp3 tag reading
import os #file ops

def getTags(songPath):
    try:
        print(songPath)
        audio = EasyID3(songPath)
        title = audio.get("title", [None])[0]
        artist = audio.get("artist", [None])[0]
        return title, artist
    except Exception as e:
        print(e)
        return None



#main

musicDir = "/appdata/Ajay/Music/" #dir containing mp3s to shuffle

for songFile in os.listdir(musicDir):
    print(getTags(musicDir+songFile))