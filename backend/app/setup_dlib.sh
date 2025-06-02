#!/bin/bash

# Update and install system dependencies
sudo apt-get update
sudo apt-get install -y build-essential cmake
sudo apt-get install -y libopenblas-dev liblapack-dev
sudo apt-get install -y libx11-dev libgtk-3-dev
sudo apt-get install -y python3-dev
sudo apt-get install -y pkg-config

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate styleclip

# Install dlib through conda
conda install -c conda-forge dlib

# If conda installation fails, try pip
if [ $? -ne 0 ]; then
    echo "Trying pip installation..."
    pip install dlib==19.22.0 --break-system-packages
fi

echo "dlib installation completed!" 