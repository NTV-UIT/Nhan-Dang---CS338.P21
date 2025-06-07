#@title Setup (may take a few minutes)
import sys
import os
from argparse import Namespace # Moved up, standard practice
import time
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt # Keep if you use it later
import torch
import torchvision.transforms as transforms

# --- Define Core Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..')) # backend/app/

E4E_DIR = os.path.join(APP_ROOT_DIR, 'encoder4editing')
STYLECLIP_DIR = os.path.join(APP_ROOT_DIR, 'StyleCLIP')
MODEL_PKL_STORAGE_DIR = os.path.join(APP_ROOT_DIR, 'model') # Where ffhq.pkl is moved

# --- sys.path Modifications ---
# Add APP_ROOT_DIR to sys.path: for imports like 'from StyleCLIP...' or 'from encoder4editing...' (if used that way)
if APP_ROOT_DIR not in sys.path:
    sys.path.insert(0, APP_ROOT_DIR)

# Add E4E_DIR to sys.path: for e4e's internal imports like 'from models...'
if E4E_DIR not in sys.path:
    sys.path.insert(0, E4E_DIR) # This allows 'from models.psp' etc. from within global_direction.py
                                # and 'from models.encoders' from within psp.py

# Add StyleCLIP/global_torch to sys.path (for dnnlib or other direct imports from there)
PATH_TO_STYLECLIP_GLOBAL_TORCH = os.path.join(STYLECLIP_DIR, 'global_torch')
if PATH_TO_STYLECLIP_GLOBAL_TORCH not in sys.path:
    sys.path.append(PATH_TO_STYLECLIP_GLOBAL_TORCH)


from utils.common import tensor2im # Resolves to E4E_DIR/utils/common.py
from models.psp import pSp         # Resolves to E4E_DIR/models/psp.py.
    
dataset_name='ffhq' #@param ['ffhq'] {allow-input: true}

# --- StyleGAN .pkl Model Download and Management ---
# Ensure target directories exist
os.makedirs(os.path.join(PATH_TO_STYLECLIP_GLOBAL_TORCH, 'model'), exist_ok=True)
os.makedirs(MODEL_PKL_STORAGE_DIR, exist_ok=True)

stylegan_config_filename = f'stylegan2-{dataset_name}-config-f.pkl'
# Temporary download path (NVIDIA's original filename)
download_destination_temp = os.path.join(PATH_TO_STYLECLIP_GLOBAL_TORCH, 'model', stylegan_config_filename)
# Final path for the model (renamed and in the project's model directory)
final_model_path_pkl = os.path.join(MODEL_PKL_STORAGE_DIR, f'{dataset_name}.pkl')

if not os.path.isfile(final_model_path_pkl):
    print(f"Model not found at {final_model_path_pkl}. Initiating download/move process.")
    if not os.path.isfile(download_destination_temp):
        print(f"Downloading {stylegan_config_filename} to {download_destination_temp}...")
        url = 'https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/'
        # Use -O to output to a specific file path
        os.system(f'wget "{url}{stylegan_config_filename}" -O "{download_destination_temp}"')
    else:
        print(f"Found pre-downloaded file at {download_destination_temp}.")

    if os.path.isfile(download_destination_temp):
        print(f"Moving {download_destination_temp} to {final_model_path_pkl}...")
        os.system(f'mv "{download_destination_temp}" "{final_model_path_pkl}"')
        print(f"Model moved to {final_model_path_pkl}.")
    else:
        # This case should ideally not be reached if wget was successful
        print(f"ERROR: Could not find {download_destination_temp} after download attempt. Cannot move.")
        # Consider exiting or raising an error here
else:
    print(f"Model {final_model_path_pkl} already exists. Skipping download and move.")


# --- CLIP and StyleCLIP Manipulator Setup ---
import clip # This import is fine here
# For 'from StyleCLIP...', APP_ROOT_DIR needs to be in sys.path and StyleCLIP be a package.
from StyleCLIP.global_torch.manipulate import Manipulator
from StyleCLIP.global_torch.StyleCLIP import GetDt,GetBoundary

device_str = "cuda" if torch.cuda.is_available() else "cpu" # Renamed to avoid conflict if 'device' used differently by Manipulator
clip_model, preprocess = clip.load("ViT-B/32", device=device_str, jit=False) # Use device_str

# --- Load StyleGAN G ---
network_pkl_to_load = final_model_path_pkl # Use the absolute path to the final model location
manipulator_device = torch.device(device_str) # Use torch.device object

M = Manipulator()
M.device = manipulator_device # Pass torch.device object
print(f"Loading StyleGAN G from: {network_pkl_to_load}")
try:
    G = M.LoadModel(network_pkl_to_load, manipulator_device)
except FileNotFoundError:
    print(f"ERROR: Manipulator.LoadModel could not find the model at {network_pkl_to_load}.")
    print("Please check the path and ensure the model was downloaded and moved correctly.")
    sys.exit(1) # Exit if model loading fails
except Exception as e:
    print(f"ERROR: An unexpected error occurred during M.LoadModel: {e}")
    sys.exit(1)

M.G = G
M.SetGParameters()
num_img = 100_000 # Consider making this smaller for initial testing
print(f"Generating {num_img} S codes (this might take a while)...")
M.GenerateS(num_img=num_img)
print("S codes generated.")
M.GetCodeMS()
np.set_printoptions(suppress=True)

# --- Load fs3.npy ---
fs3_file_path = os.path.join(PATH_TO_STYLECLIP_GLOBAL_TORCH, 'npy', dataset_name, 'fs3.npy')
print(f"Loading fs3.npy from: {fs3_file_path}")
if not os.path.isfile(fs3_file_path):
    print(f"ERROR: fs3.npy not found at {fs3_file_path}. Please ensure it exists.")
    # Potentially download fs3.npy if it's also a remote resource and not found
    # For now, assume it's present or raise an error.
    sys.exit(1)
fs3 = np.load(fs3_file_path)

print("Setup complete. fs3 loaded.")
# You can now use M, G, clip_model, preprocess, fs3