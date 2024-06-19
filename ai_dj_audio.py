from transformers import AutoProcessor, BarkModel
from scipy.io import wavfile
from pydub import AudioSegment#audio concating
import os


def setupAudioModel():

    # Load processor and model
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark").to("cuda")
    model = model.to_bettertransformer()
    return model,processor

def generateAudio(text,songX,songY,musicDir,model,processor):
    
    illegalChars=["/","\\",".","|","!"]#chars that can screw up the file output
    outName="_Transition_"+songX+" - "+songY
    
    for illegalChar in illegalChars:
        outName=outName.replace(illegalChar," ")
    outName=outName+".wav" #adds file extension afterwards so not affected by char removal
    
    print("Generating audio, outputting to",outName)
    voice_preset = "v2/en_speaker_8"
    # Process input text
    inputs = processor(text, voice_preset=voice_preset, return_tensors="pt")
    inputs = {key: value.to("cuda") for key, value in inputs.items()}    # Ensure inputs are on the correct device
    audio_array = model.generate(**inputs)

    # Move audio array to CPU and convert to float32 numpy array
    audio_array = audio_array.cpu().float().numpy().squeeze()

    # Normalize the audio array to the range [-1, 1]
    audio_array = audio_array / max(abs(audio_array))

    # Get the sample rate and save the file
    sample_rate = model.generation_config.sample_rate
    wavfile.write(musicDir+outName, rate=sample_rate, data=audio_array)
    return outName #returns the filename (Not full path)

def concatAudio(playbackOrder,musicDir):#concats audio files and exports as one
    print("Joining audio files")
    printPlaybackOrder(playbackOrder)
    blendDuration=500 #milliseconds to blend between songs
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