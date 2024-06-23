# Use the official CUDA base image provided by NVIDIA to skip some driver setup
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .

#Installs reqs

# Install Python, pip, and ffmpeg
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg
#installs pytorch
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 
# Install remaining python libs
RUN pip3 install --no-cache-dir -r requirements.txt

# api key needed to download models from huggingface, replace this with your key with -e HUGGINGFACE_KEY yourKeyHere when using docker run. A key can be generated at https://huggingface.co/settings/tokens
ARG HUGGINGFACE_KEY=1234 

# Copies rest of repo into the container
COPY . .

RUN python3 -c 'from huggingface_hub import HfFolder; HfFolder.save_token("<${HUGGINGFACE_KEY}>")'
# RUN huggingface-cli login $HUGGINGFACE_KEY
# Runs the main command, allowing for args to be passed through
ENTRYPOINT ["python3", "ai_dj_main.py"]
