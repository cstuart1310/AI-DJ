#import ai_dj_text
import ai_dj_audio
from mutagen.easyid3 import EasyID3 #mp3 tag reading
import os #file ops
import subprocess
import argparse #args
import random #shuffling

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
if shuffleSongs:
    songs = random.shuffle(songs)#shuffles order if wanted
    playbackOrder=songs#array of mp3 playback, will later have transitions inserted then mp3's concated

for songIndex, songFile in enumerate(songs[:-1]):#iterates through until the last 2 songs (Final transition point)
    songX, nameX = (getTags(musicDir+songFile))#index
    songY, nameY = (getTags(musicDir+songs[songIndex+1]))#next in list after index

    if all(noneCheck is not None for noneCheck in [songX,songY,nameX,nameY]):#if all vars have a non-none value
        print("Transitioning from:",songX,"by",nameX,"to",songY,"by",nameY)
        with open(transitionsFile,"a") as transitionFile:
            transitionFile.write((songX+"|"+songY+"|"+nameX+"|"+nameY+"\n"))#writes song names and artist names to txt for passing to other script
subprocess.run("python3 /appdata/Ajay/AI-DJ/ai_dj_text.py",shell=True)#Runs the text generator via subprocess. Subprocess needed due to memory leak if func called then "cleaned up". Text generated is outputted to txt


print("_"*30)
print("Generating Audio")
audioModel, audioProcessor = ai_dj_audio.setupAudioModel()#can use ai_dj_audio as a lib as no memory leak issue
for response in (open(responsesFile,"r").readlines()):#for each line of ai generated text
    response=response.split("|")#lines also contain song names in format: songX | songY | generatedText
    songX=response[0]
    songY=response[1]
    transitionText=response[2]
    
    print(songX,"->",songY)
    print("Transition Text:",transitionText)
    ai_dj_audio.generateAudio(transitionText,songX,songY,musicDir,audioModel,audioProcessor)#generates audio as mp3


    
print("____________________")
