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

def getSongs(musicDir,searchSubdirs):
    print("Searching for songs")
    songs=[]#init array in case returns no songs    
    
    if searchSubdirs==True:#searches through subdirs for songs
        for currentPath, subdirs, filesInCurrentPath in os.walk(musicDir):#loops through each subdir
            for song in filesInCurrentPath:#for each file in the subdir
                if song.endswith(".mp3"):#if file is an mp3
                    songs.append(os.path.join(currentPath,song))
    
    elif searchSubdirs==False:#Only looks through given path for songs
        songs=os.listdir(musicDir)#lists songs in given dir

    print(len(songs),"songs found in",musicDir)
    if len(songs)<2:
        print("Minimum songs for processing is 2. Exiting program.")
        quit()#kills the program as no processing to be done without songs
    return songs #Returns a non-empty array of songs
        
    


#args
cwd=os.getcwd() #dir containing this script (And hopefully the others)

argparser=argparse.ArgumentParser()
argparser.add_argument("--music",default="/Music/",help="Directory containing songs to transition between")
argparser.add_argument("--intermissions",type=int,default=1,help="Number of songs to play before an intermission")
argparser.add_argument("--shuffle",default=False,action=argparse.BooleanOptionalAction,help="Shuffle the order of songs before generating radio, or keep them in alphabetical order")
argparser.add_argument("--subdirs",default=False,action=argparse.BooleanOptionalAction,help="Whether or not to dig through subdirs of music path to find songs")
argparser.add_argument("--output",default=cwd)
argparser.add_argument("--length",default=None,type=int,help="Number of songs to process out of those found in the given directory")
args=argparser.parse_args()

musicDir = args.music  # dir containing mp3s
intermissions = args.intermissions
shuffleSongs = args.shuffle
outputDir=args.output
songLength=args.length
searchSubdirs=args.subdirs

#adds / to end of dir path if not already there by user
if musicDir.split()[-1] !="/":
    musicDir=musicDir+"/"
    
if outputDir.split()[-1] !="/":
    outputDir=outputDir+"/"

#shows arg values
print("Music Directory:",musicDir)
print("Songs between intermissions:",intermissions)
print("Number of files to process:",songLength)
print("Shuffle playlist?:",shuffleSongs)
print("Search subdirs?:",searchSubdirs)

#main
transitionsFile=cwd+"/transitions.txt"
responsesFile=cwd+"/responses.txt"
audioExtensions=[".mp3",".wav"]#array of valid audio file extensions
cleanupFiles=[]#files to delete after processing

resetTxts()#clears text files

songs=getSongs(musicDir,searchSubdirs)
    
playbackOrder=[]#array of order of audios to play, starts empty so can skip untagged mp3s
if shuffleSongs==True:
    print("Songs have been shuffled")
    random.shuffle(songs)#shuffles order if wanted

if songLength==None or songLength>len(songs):#If song length is default value or greater than allowed
    songLength=len(songs)#replaces None with length of array so all songs are iterated through
    
for songIndex, songFile in enumerate(songs[0:songLength]):#iterates through the chosen number of songs
        if os.path.splitext(songFile)[1].lower() in audioExtensions:#checks to make sure file is a valid audio file (Also filters out subdirs)
            if songIndex+intermissions<len(songs) and songIndex+1<songLength:#while there is songs enough for another intermission, and not too many to be out of the range
                songX, nameX = (getTags(songFile))#tags of songindex
                songY, nameY = (getTags(songs[songIndex+1]))#tags of next in list after index
                if all(noneCheck is not None for noneCheck in [songX,songY,nameX,nameY]):#if all vars have a non-none value
                    print("Transitioning from:",songX,"by",nameX," ---> ",songY,"by",nameY)
                    playbackOrder.append(songFile)
                    transitionName=generateTransitionName(songX,songY)
                    playbackOrder.append(musicDir+transitionName) #inserts transition file name between index pointer and index+1 (between songXs and songY)
                    with open(transitionsFile,"a") as transitionFile:
                        transitionFile.write((songX+"|"+songY+"|"+nameX+"|"+nameY+"|"+transitionName+"\n"))#writes song names and artist names to txt for passing to other script
            else:#final song in array or final song that can fit a transition
                print("Can't fit any more transitions/songs, adding",songFile,"to playback list")
                playbackOrder.append(songFile)#adds songs to playback order without generating transitions
                

ai_dj_audio.printPlaybackOrder(playbackOrder)
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
    cleanupFiles.append(ai_dj_audio.generateAudio(transitionText,songX,songY,musicDir,audioModel,audioProcessor))#generates audio as mp3, and appends it to be deleted later
    
print("_"*30)
ai_dj_audio.concatAudio(playbackOrder,musicDir,outputDir)

print("Cleaning up!")
for cleanupFile in cleanupFiles:
    print("Deleting:",cleanupFile)
    os.remove(cleanupFile)