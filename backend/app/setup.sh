#!/bin/bash

echo "Starting Python reinstallation process..."

# # Deactivate current environment and remove it
# echo "Removing existing environment..."
# conda deactivate
# conda env remove -n styleclip -y

# Create new environment with Python 3.8
echo "Creating new environment with Python 3.8..."
conda create -n styleclip python=3.8 -y

# Activate new environment
echo "Activating new environment..."
eval "$(conda shell.bash hook)"
conda activate styleclip

# Install PyTorch and torchvision
echo "Installing PyTorch and torchvision..."
conda install pytorch==1.7.1 torchvision==0.8.2 cudatoolkit=11.0 -c pytorch -y

# Install core dependencies through conda
echo "Installing core dependencies..."
conda install -c conda-forge dlib -y
conda install -c conda-forge numpy pillow matplotlib -y
conda install -c conda-forge scipy scikit-learn -y
conda install -c conda-forge opencv -y

# Install API dependencies with specific versions
echo "Installing API dependencies..."
pip install "fastapi==0.95.2"
pip install "uvicorn==0.22.0"
pip install "python-multipart==0.0.6"
pip install "pydantic==1.10.8"
pip install "typing-extensions==4.5.0"

# Install remaining packages through pip
echo "Installing remaining packages..."
pip install gdown
pip install tqdm
pip install tensorflow==2.10.0
pip install git+https://github.com/openai/CLIP.git
pip install git+https://github.com/NVlabs/stylegan2-ada-pytorch.git

# Verify installation
echo "Verifying installation..."
python -c "import torch; import torchvision; import dlib; import numpy; import PIL; import matplotlib; import cv2; import fastapi; import pydantic; print('Python version:', __import__('sys').version)"
python -c "import torch; import torchvision; import dlib; print('All packages imported successfully!')"

echo "Installation completed! Please activate the environment with: conda activate styleclip" 