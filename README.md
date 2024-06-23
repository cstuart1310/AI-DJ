# Ajay - (AI-DJ)
Generates a custom radio show with realistic speech transitions between songs.

**Currently Proof of Concept, and very VERY early in development**

## Example output
[![Example DJ video](https://i.ytimg.com/vi/beMPSie01Mk/maxresdefault.jpg?sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgZShlMA8=&rs=AOn4CLCYURGrdUDDAYM1vLa8KPsufswYvA)](https://www.youtube.com/watch?v=/beMPSie01Mk)

## Requirements (Local and docker install)
[Download NVIDIA drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/) for your system
A huggingFace account with an [API key](https://huggingface.co/settings/tokens)

## Install (Local)
Download the repo and cd into it

```git clone https://github.com/cstuart1310/AI-DJ.git && cd AI-DJ```

Install python requirements

```pip install -r requirements.txt```

Login to huggingface

```huggingface-cli login --token yourTokenHere```

Run the script

```python ai_dj_main.py --music /path/to/music/```

## Install (Docker)
[Download the CUDA Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to allow CUDA to interface with docker

Download the repo and cd into it

```git clone https://github.com/cstuart1310/AI-DJ.git && cd AI-DJ```

Build the docker image, passing your huggingface api key generated from [HuggingFace.co](https://huggingface.co/settings/tokens)

```docker build . --build-arg HUGGINGFACE_KEY="yourkeyinquotes"```

Run the docker image, passing into it the path for models to download to/currently exist. Default downloads for huggingface go to /root/.cache/huggingface/hub
```docker run -v /path/to/music:/Music -v /path/to/models/:/root/.cache/huggingface/hub --gpus all ai-dj ```

## Resources
Current LLM used for all tests: [Storytime-13B](https://huggingface.co/TheBloke/storytime-13B-GPTQ)

Current Text-to-audio model: [Bark](https://huggingface.co/spaces/suno/bark)
