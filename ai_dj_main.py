import ai_dj_audio #can import as a lib, text cannot import as lib due to weird memory leak issues
from mutagen.easyid3 import EasyID3 #mp3 tag reading
import os #file ops
import subprocess
import argparse #args
import random #shuffling
from pydub import AudioSegment#audio concating


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

def concatAudio(playbackOrder):#concats audio files and exports as one
    print("Joining audio files")
    printPlaybackOrder(playbackOrder)
    blendDuration=2000 #milliseconds to blend between songs
    combined = AudioSegment.empty() #init combination of audio

    for audioIndex, audioFile in enumerate(playbackOrder): #for each file in musicDir (Incl transitions)
        audioFile=musicDir+audioFile #Adds full path to filename
        print(audioFile)
        audioExtension = os.path.splitext(audioFile)[1].lower()
        
        if audioExtension == ".mp3":
            audio = AudioSegment.from_mp3(audioFile)
        elif audioExtension == ".wav":
            audio = AudioSegment.from_wav(audioFile)
        else:
            print("Unsupported filetype:",audioFile)
        if audioIndex == 0: #first audio file begins the out file
            combined = audio
        else: #any audio files from index 1: are concated
            combined = combined.append(audio, crossfade=blendDuration)
            combined.export("Ajay_Radio.mp3", format="mp3")#exports the file as an mp3
    
def printPlaybackOrder(playbackOrder):
    print("Playback Order:")
    for audioIndex, audioFile in enumerate(playbackOrder):
        print(str(audioIndex+1)+"."+audioFile)

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
playbackOrder=[]#array of order of audios to play, starts empty so can skip untagged mp3s
if shuffleSongs:
    songs = random.shuffle(songs)#shuffles order if wanted

for songIndex, songFile in enumerate(songs):#iterates through until the last 2 songs (Final transition point)
    
    if songIndex+1<len(songs):#while there is one song in front of the index location
        songX, nameX = (getTags(musicDir+songFile))#index
        songY, nameY = (getTags(musicDir+songs[songIndex+1]))#next in list after index
        if all(noneCheck is not None for noneCheck in [songX,songY,nameX,nameY]):#if all vars have a non-none value
            print("Transitioning from:",songX,"by",nameX,"to",songY,"by",nameY)
            print("playback len",len(playbackOrder))
            playbackOrder.append(songFile)
            transitionName=generateTransitionName(songX,songY)
            playbackOrder.append(transitionName) #inserts transition file name between index pointer and index+1 (between songXs and songY)
            with open(transitionsFile,"a") as transitionFile:
                transitionFile.write((songX+"|"+songY+"|"+nameX+"|"+nameY+"|"+transitionName+"\n"))#writes song names and artist names to txt for passing to other script
    else:#final song in the array
        playbackOrder.append(songFile)#adds final song to end of array
            
printPlaybackOrder(playbackOrder)
subprocess.run("python3 /appdata/Ajay/AI-DJ/ai_dj_text.py",shell=True)#Runs the text generator via subprocess. Subprocess needed due to memory leak if func called then "cleaned up". Text generated is outputted to txt



print("_"*30)
print("Generating Audio")
audioModel, audioProcessor = ai_dj_audio.setupAudioModel()#can use ai_dj_audio as a lib as no memory leak issue
for response in (open(responsesFile,"r").readlines()):#for each line of ai generated text
    response=response.split("|")#lines also contain song names in format: songX | songY | generatedText
    songX=response[0]
    songY=response[1]
    transitionText=response[2]
    audioFileName=response[3]
    
    print(songX,"->",songY)
    print("Transition Text:",transitionText)
    print("Transition file name:")
    ai_dj_audio.generateAudio(transitionText,songX,songY,musicDir,audioModel,audioProcessor)#generates audio as mp3
print("_"*30)

concatAudio(playbackOrder)