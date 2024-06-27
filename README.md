# Ajay - (AI-DJ)
Generates a custom radio show with realistic speech transitions between songs.

**Currently Proof of Concept, and very VERY early in development**

Has only been tested on a Debian system so far, may or may not work on Windows.
## Example output (Video)
[![Example DJ video](https://i.ytimg.com/vi/beMPSie01Mk/maxresdefault.jpg?sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgZShlMA8=&rs=AOn4CLCYURGrdUDDAYM1vLa8KPsufswYvA)](https://www.youtube.com/watch?v=beMPSie01Mk)

## Installation
### Requirements (Local and docker install)
[NVIDIA drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/) for your system

A HuggingFace account with an [API key](https://huggingface.co/settings/tokens)

### Install (Local)
Download the repo and cd into it

```git clone https://github.com/cstuart1310/AI-DJ.git && cd AI-DJ```

Install python requirements

```pip install -r requirements.txt```

Login to huggingface

```huggingface-cli login --token yourTokenHere```

Run the script

```python ai_dj_main.py --music /path/to/music/```

### Install (Docker)
[Download the CUDA Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to allow CUDA to interface with docker

Download the repo and cd into it

```git clone https://github.com/cstuart1310/AI-DJ.git && cd AI-DJ```

Build the docker image, passing your huggingface api key generated from [HuggingFace.co](https://huggingface.co/settings/tokens)

```docker build . --build-arg HUGGINGFACE_KEY="yourkeyinquotes"```

Run the docker image, passing into it the path for models to download to/currently exist. Default downloads for huggingface go to /root/.cache/huggingface/hub
```docker run -v /path/to/music:/Music -v /path/to/models/:/root/.cache/huggingface/hub --gpus all ai-dj ```

## Command-Line Arguments
* ```--music /path/to/music``` The directory containing MP3s to transition between (Default: /Music)

* ```--intermissions 1/2/3/...``` The number of songs to play before an intermission. (Default: 1)

* ```--shuffle``` Shuffles the order of the files from the music folder

* ```--output /path/to/output``` The directory to output the combined MP3 of transitions and songs to

* ```--length 1/2/3/...``` The number of songs to process from the given directory

* ```--subdirs``` Searches subdirs of the music dir for mp3's, as opposed to just the given music dir

### Example run with arguments
#### Local run: 
**Full Command**

```python ai_dj_main.py --music /home/music --intermissions 5 --shuffle --output /home/dj --length 50 --subdirs```

**Breakdown**

* ```--music /home/music``` Reads music from /home/music

* ```--intermissions 5``` Plays 5 songs and then a transition

* ```--shuffle``` Shuffles the order of the found songs

* ```--output /home/dj``` Outputs the combined MP3 file to /home/dj

* ```--length 50``` Only processes 50 songs found in /home/music (Or the maximum if less than 50 are found)

* ``` --subdirs``` Looks through subdirectories of /home/music for songs

#### Docker Run:
**Full Command**

 ```docker run -v /home/music:/inContainer/music -v /root/.cache/huggingface/hub:/root/.cache/huggingface/hub --gpus all ai-dj --music /inContainer/music --intermissions 5 --shuffle --output /inContainer/output --length 50```

**Breakdown**

* ``` -v /home/music:/inContainer/music``` Binds /home/music (Local directory) to /inContainer/music (Directory within the docker container)

* ``` -v /root/.cache/huggingface/hub:/root/.cache/huggingface/hub``` Binds /root/.cache/huggingface/hub (Local directory) to /root/.cache/huggingface/hub (Directory within the docker container)

* ```--gpus all``` Uses any/all GPUs available to the container

* ```ai-dj``` Uses the ai-dj image (If this image is unavailable, you must build it locally)

* ```--music /inContainer/music``` Reads music from /inContainer/music (Directory found within the container which binds to /home/music)

* ``` --intermissions 5``` Plays 5 songs and then an intermission

* ```--shuffle```Shuffles the order of the found songs

* ```--output /inContainer/output``` Outputs the combined MP3 file to /inContainer/output (Directory within the docker container)

* ```--length 50``` Only processes 50 songs found in /inContainer/music

## Resources
Current LLM used for all tests: [Storytime-13B](https://huggingface.co/TheBloke/storytime-13B-GPTQ)

Current Text-to-audio model: [Bark](https://huggingface.co/spaces/suno/bark)
