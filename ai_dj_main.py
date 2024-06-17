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
    
def resetTxts():#clears files on new run
    open(transitionsFile, 'w').close()
    open(responsesFile, 'w').close()

#main
transitionsFile="transitions.txt"
responsesFile="responses.txt"
resetTxts()
musicDir = "/appdata/Ajay/Music/" #dir containing mp3s to shuffle
transitionSkips=1 #number of songs to iterate for transitions

songs=os.listdir(musicDir)
transitions=[]
for songIndex, songFile in enumerate(songs[:-1]):#iterates through until the last 2 songs (Final transition point)
    songX, nameX = (getTags(musicDir+songFile))#index
    songY, nameY = (getTags(musicDir+songs[songIndex+1]))#next in list after index

    if all(noneCheck is not None for noneCheck in [songX,songY,nameX,nameY]):#if all vars have a non-none value
        print("Transitioning from:")
        print(songX,"by",nameX)
        print("to")
        print(songY,"by",nameY)
        with open(transitionsFile,"a") as transitionFile:
            transitionFile.write((songX+"|"+songY+"|"+nameX+"|"+nameY+"\n"))
        transitions.append([songX,nameX,songY,nameY])
subprocess.run("python3 /appdata/Ajay/AI-DJ/ai_dj_text.py",shell=True)#subprocess needed due to memory leak if func called then "cleaned up"


print("_"*30)
print("Generating Audio")
audioModel, audioProcessor = ai_dj_audio.setupAudioModel()
for response in (open(responsesFile,"r").readlines()):
    print(response)
    response=response.split("|")
    print(response)
    songX=response[0]
    songY=response[1]
    transitionText=response[2]
    
    print(songX,"->",songY)
    print("Transition Text:",transitionText)
    ai_dj_audio.generateAudio(transitionText,songX,songY,musicDir,audioModel,audioProcessor)

    
print("____________________")