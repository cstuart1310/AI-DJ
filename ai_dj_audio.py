from transformers import AutoProcessor, BarkModel
from scipy.io import wavfile
import torch

def setupAudioModel():

    # Load processor and model
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark").to("cuda")
    model = model.to_bettertransformer()
    return model,processor

def generateAudio(text,songX,songY,musicDir,model,processor):
    
    illegalChars=["/","\\",".","|"]#chars that can screw up the file output
    outName="_Transition_"+songX+" - "+songY
    
    for illegalChar in illegalChars:
        outName=outName.replace(illegalChar," ")
    outName=musicDir+outName+".wav" #adds file extension afterwards so not affected by char removal
    
    print("Generating audio, outputting to",outName)
    voice_preset = "v2/en_speaker_8"
    # Process input text
    inputs = processor(text, voice_preset=voice_preset, return_tensors="pt")

    # Ensure inputs are on the correct device
    inputs = {key: value.to("cuda") for key, value in inputs.items()}

    # Generate audio without mixed precision
    audio_array = model.generate(**inputs)

    # Move audio array to CPU and convert to float32 numpy array
    audio_array = audio_array.cpu().float().numpy().squeeze()

    # Normalize the audio array to the range [-1, 1]
    audio_array = audio_array / max(abs(audio_array))

    # Get the sample rate and save the file
    sample_rate = model.generation_config.sample_rate
    wavfile.write(outName, rate=sample_rate, data=audio_array)
    return outName
