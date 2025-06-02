from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import argparse
import time
import os
import sys
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
import tensorflow as tf
import clip
import pickle
import copy
from gdown import download as drive_download
import matplotlib.pyplot as plt
from global_directions.MapTS import GetFs, GetBoundary, GetDt
from global_directions.manipulate import Manipulator
from utils.common import tensor2im
from models.psp import pSp
from argparse import Namespace

# Add StyleCLIP to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
styleclip_dir = os.path.join(backend_dir, 'StyleCLIP')
sys.path.append(styleclip_dir)

# Create pretrained_models directory if it doesn't exist
pretrained_dir = os.path.join(current_dir, 'pretrained_models')
os.makedirs(pretrained_dir, exist_ok=True)

def setup_device():
    """Setup and return the device (CPU/GPU)"""
    return "cuda" if torch.cuda.is_available() else "cpu"

def load_clip_model(device):
    """Load and return the CLIP model"""
    return clip.load("ViT-B/32", device=device)

def download_pretrained_model():
    """Download the pretrained e4e model if not exists"""
    model_path = os.path.join(pretrained_dir, 'e4e_ffhq_encode.pt')
    if not os.path.exists(model_path):
        drive_download("https://drive.google.com/uc?id=1O8OLrVNOItOJoNGMyQ8G8YRTeTYEfs0P", 
                      model_path, 
                      quiet=False)

def load_e4e_model():
    """Load and return the e4e model"""
    model_path = os.path.join(pretrained_dir, 'e4e_ffhq_encode.pt')
    ckpt = torch.load(model_path, map_location='cpu')
    opts = ckpt['opts']
    opts['checkpoint_path'] = model_path
    opts = Namespace(**opts)
    net = pSp(opts)
    net.eval()
    net.cuda()
    return net

def run_alignment(image_path):
    """Align face in the image using dlib"""
    import dlib
    from utils.alignment import align_face
    
    predictor_path = os.path.join(pretrained_dir, 'shape_predictor_68_face_landmarks.dat')
    if not os.path.exists(predictor_path):
        os.system(f'wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 -O {predictor_path}.bz2')
        os.system(f'bzip2 -dk {predictor_path}.bz2')
    
    predictor = dlib.shape_predictor(predictor_path)
    aligned_image = align_face(filepath=image_path, predictor=predictor)
    return aligned_image

def process_image(image_path, experiment_type="ffhq_encode"):
    """Process and return the aligned/transformed image"""
    original_image = Image.open(image_path).convert("RGB")
    
    if experiment_type == "ffhq_encode":
        input_image = run_alignment(image_path)
    else:
        input_image = original_image
    
    return input_image.resize((256, 256))

def run_on_batch(inputs, net):
    """Run inference on a batch of images"""
    with torch.no_grad():
        images, latents = net(inputs.to("cuda").float(), randomize_noise=False, return_latents=True)
    return images, latents

def manipulate_image(latents, M, neutral_text, target_text, beta=0.15, alpha=4.1):
    """Manipulate the image using StyleCLIP"""
    classnames = [target_text, neutral_text]
    dt = GetDt(classnames, M.model)
    
    M.alpha = [alpha]
    boundary_tmp2, c = GetBoundary(M.fs3, dt, M, threshold=beta)
    codes = M.MSCode(latents, boundary_tmp2)
    out = M.GenerateImg(codes)
    return Image.fromarray(out[0,0])

def display_results(original, manipulated):
    """Display original and manipulated images side by side"""
    plt.figure(figsize=(20,7), dpi=100)
    plt.subplot(1,2,1)
    plt.imshow(original)
    plt.title('original')
    plt.axis('off')
    plt.subplot(1,2,2)
    plt.imshow(manipulated)
    plt.title('manipulated')
    plt.axis('off')
    plt.show()

def main():
    # Setup
    device = setup_device()
    model, preprocess = load_clip_model(device)
    download_pretrained_model()
    net = load_e4e_model()
    
    # Initialize manipulator
    M = Manipulator(dataset_name='ffhq')
    fs3_path = os.path.join(pretrained_dir, 'fs3.npy')
    if not os.path.exists(fs3_path):
        # Copy fs3.npy from StyleCLIP directory if it exists
        styleclip_fs3 = os.path.join(styleclip_dir, 'pretrained_models/fs3.npy')
        if os.path.exists(styleclip_fs3):
            import shutil
            shutil.copy2(styleclip_fs3, fs3_path)
        else:
            raise FileNotFoundError("fs3.npy not found in StyleCLIP pretrained models")
    M.fs3 = np.load(fs3_path)
    
    # Process image
    image_path = "./data/00000.jpg"
    input_image = process_image(image_path)
    
    # Transform image
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    transformed_image = transform(input_image)
    
    # Get latents
    images, latents = run_on_batch(transformed_image.unsqueeze(0), net)
    w_plus = latents.cpu().detach().numpy()
    dlatents_loaded = M.W2S(w_plus)
    
    # Manipulate image
    neutral_text = "face with eyes"
    target_text = "face with blue eyes"
    manipulated_image = manipulate_image(dlatents_loaded, M, neutral_text, target_text)
    
    # Display results
    display_results(input_image, manipulated_image)

if __name__ == "__main__":
    main()