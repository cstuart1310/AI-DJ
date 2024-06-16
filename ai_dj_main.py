import generateText
from mutagen.easyid3 import EasyID3 #mp3 tag reading
import os #file ops

def getTags(songPath):
    try:
        audio = EasyID3(songPath)
        title = audio.get("title", [None])[0]
        artist = audio.get("artist", [None])[0]
        return title, artist
    except Exception as e:
        print(e)
        return None,None



#main

musicDir = "/appdata/Ajay/Music/" #dir containing mp3s to shuffle
transitionSkips=1 #number of songs to iterate for transitions

songs=os.listdir(musicDir)
responses=[]
for songIndex, songFile in enumerate(songs[:-1]):#iterates through until the last 2 songs (Final transition point)
    try:
        
        songX, nameX = (getTags(musicDir+songFile))#index
        songY, nameY = (getTags(musicDir+songs[songIndex+1]))#next in list after index

        print("Transitioning from:")
        print(songX,"by",nameX)
        print("to")
        print(songY,"by",nameY)
        responses.append(generateText.genResponse(songX,nameX,songY,nameY))
    except:
        for response in responses:
            print(response)
    
print("____________________")