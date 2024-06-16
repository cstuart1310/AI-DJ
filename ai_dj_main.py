#import ai_dj_text
import ai_dj_audio
from mutagen.easyid3 import EasyID3 #mp3 tag reading
import os #file ops
import torch #only used to clear VRAM
import gc
import subprocess

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
transitions=[["songX","songY","Hello world this is a speech test"]]
for songIndex, songFile in enumerate(songs[:-1]):#iterates through until the last 2 songs (Final transition point)
    songX, nameX = (getTags(musicDir+songFile))#index
    songY, nameY = (getTags(musicDir+songs[songIndex+1]))#next in list after index

    print("Transitioning from:")
    print(songX,"by",nameX)
    print("to")
    print(songY,"by",nameY)
    with open("transitions.txt","a") as transitionFile:
        transitionFile.write((songX+"|"+songY+"|"+nameX+"|"+nameY+"\n"))
    subprocess.run("python3 /appdata/Ajay/AI-DJ/ai_dj_text.py",shell=True)#subprocess needed due to memory leak if func called then "cleaned up"
    transitions.append([songX,nameX,songY,nameY])
    
print("_"*30)
print("Generating Audio")
audioModel, audioProcessor = ai_dj_audio.setupAudioModel()
for transition in open("responses.txt","r").readlines():
    songX="songX"
    songY="songY"
    
    print(songX,"->",songY)
    print(transition)
    
    ai_dj_audio.generateAudio(transition,songX,songY,musicDir,audioModel,audioProcessor)

    
print("____________________")