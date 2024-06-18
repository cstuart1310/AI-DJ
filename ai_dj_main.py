#import ai_dj_text
import ai_dj_audio
from mutagen.easyid3 import EasyID3 #mp3 tag reading
import os #file ops
import subprocess
import argparse #args

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


#args
argparser=argparse.ArgumentParser()
argparser.add_argument("--songs",default="/appdata/Ajay/Music/",help="Directory containing songs to transition between")
argparser.add_argument("--intermissions",type=int,default=1,help="Number of songs to play between each AI intermission before the next intermission")
argparser.add_argument("--shuffle",default=False,help="Shuffle the order of songs before generating radio, or keep them in alphabetical order")
args=argparser.parse_args()
musicDir = args.songs  # dir containing mp3s
intermissions = args.intermissions
shuffleSongs = args.shuffle

print("Music Directory:",musicDir)
print("Songs between intermissions:",intermissions)
print("Shuffle playlist?:",shuffleSongs)

#main
transitionsFile="transitions.txt"
responsesFile="responses.txt"
resetTxts()

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
