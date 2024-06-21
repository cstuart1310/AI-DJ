# Use the official CUDA base image provided by NVIDIA to skip some driver setup
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .

# Install Python, pip, and ffmpeg
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg
#installs pytorc
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Install remaining python libs
RUN pip3 install --no-cache-dir -r requirements.txt

# Copies rest of repo into the container
COPY . .

# Runs the main command, allowing for args to be passed through
ENTRYPOINT ["python3", "ai_dj_main.py"]
