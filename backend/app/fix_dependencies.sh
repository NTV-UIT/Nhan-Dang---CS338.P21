#!/bin/bash

echo "Fixing dependency conflicts..."

# Uninstall conflicting packages
echo "Uninstalling conflicting packages..."
pip uninstall -y typing-extensions tensorflow fastapi uvicorn python-multipart pydantic pydantic-core

# Install compatible versions
echo "Installing compatible versions..."
pip install "typing-extensions>=4.6.0,!=4.7.0"
pip install "tensorflow==2.10.0"
pip install "fastapi==0.95.2"
pip install "uvicorn==0.22.0"
pip install "python-multipart==0.0.6"
pip install "pydantic==1.10.8"

# Verify installation
echo "Verifying installation..."
python -c "import tensorflow; import fastapi; import pydantic; print('All packages installed successfully!')"

echo "Done!" 