import ai_dj_audio #can import as a lib, text cannot import as lib due to weird memory leak issues
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

def generateTransitionName(songX,songY):
    illegalChars=["/","\\",".","|","!"]#chars that can screw up the file output
    outName="_Transition_"+songX+" - "+songY
    for illegalChar in illegalChars:
        outName=outName.replace(illegalChar," ")
    outName=outName+".wav" #adds file extension afterwards so not affected by char removal
    return outName


    

cwd=os.getcwd() #dir containing this script (And hopefully the others)

#args
argparser=argparse.ArgumentParser()
argparser.add_argument("--music",default=(cwd+"/"),help="Directory containing songs to transition between")
argparser.add_argument("--intermissionless",type=int,default=1,help="Number of songs to play between each AI intermission before the next intermission")
argparser.add_argument("--shuffle",default=False,help="Shuffle the order of songs before generating radio, or keep them in alphabetical order")
argparser.add_argument("--output",default=cwd)
argparser.add_argument("--length",default=None,type=int,help="Number of songs to process out of those found in the given directory")
args=argparser.parse_args()

musicDir = args.music  # dir containing mp3s
intermissionless = args.intermissionless
shuffleSongs = args.shuffle
songLength=args.length

if musicDir.split()[-1] !="/":
    musicDir=musicDir+"/"

print("Music Directory:",musicDir)
print("Songs between intermissions:",intermissionless)
print("Shuffle playlist?:",shuffleSongs)

#main
transitionsFile=cwd+"/transitions.txt"
responsesFile=cwd+"/responses.txt"
resetTxts()

songs=os.listdir(musicDir)
playbackOrder=[]#array of order of audios to play, starts empty so can skip untagged mp3s
if shuffleSongs:
    print("Shuffled songs")
    random.shuffle(songs)#shuffles order if wanted

if songLength==None:#If song length is default value
    songLength=len(songs)#replaces None with length of array so all songs are iterated through

for songIndex, songFile in enumerate(songs[0:songLength]):#iterates through the chosen number of songs
    print(musicDir+songFile)
    if os.path.isdir(musicDir+songFile)==False:#check to make sure song file isn't actually a dir
        if songIndex+1<len(songs):#while there is one song in front of the index location (Allowing for a transition)
            songX, nameX = (getTags(musicDir+songFile))#index
            songY, nameY = (getTags(musicDir+songs[songIndex+1]))#next in list after index
            if all(noneCheck is not None for noneCheck in [songX,songY,nameX,nameY]):#if all vars have a non-none value
                print("Transitioning from:",songX,"by",nameX,"to",songY,"by",nameY)
                playbackOrder.append(songFile)
                transitionName=generateTransitionName(songX,songY)
                playbackOrder.append(transitionName) #inserts transition file name between index pointer and index+1 (between songXs and songY)
                with open(transitionsFile,"a") as transitionFile:
                    transitionFile.write((songX+"|"+songY+"|"+nameX+"|"+nameY+"|"+transitionName+"\n"))#writes song names and artist names to txt for passing to other script
        else:#final song in the array
            playbackOrder.append(songFile)#adds final song to end of array
            
subprocess.run(("python3 "+cwd+"/ai_dj_text.py"),shell=True)#Runs the text generator via subprocess. Subprocess needed due to memory leak if func called then "cleaned up". Text generated is outputted to txt

print("_"*30)
print("Generating Audio")
audioModel, audioProcessor = ai_dj_audio.setupAudioModel()#can use ai_dj_audio as a lib as no memory leak issue
for response in (open(responsesFile,"r").readlines()):#for each line of ai generated text
    response=response.split("|")#lines also contain song names in format: songX | songY | generatedText | audioFileName
    songX=response[0]
    songY=response[1]
    transitionText=response[2]
    audioFileName=response[3]
    
    print(songX,"->",songY)
    print("Transition Text:",transitionText)
    print("Transition file name:")
    ai_dj_audio.generateAudio(transitionText,songX,songY,musicDir,audioModel,audioProcessor)#generates audio as mp3
print("_"*30)

ai_dj_audio.concatAudio(playbackOrder,musicDir)