from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import sys
import uuid
import shutil
from pathlib import Path
from typing import Optional
import argparse
import torch
from argparse import Namespace
from enum import Enum
import base64
import tempfile
import io

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Add StyleCLIP to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
styleclip_dir = os.path.join(backend_dir, 'StyleCLIP')
sys.path.append(styleclip_dir)

# Add encoder4editing to Python path
encoder4editing_dir = os.path.join(os.path.dirname(styleclip_dir), 'encoder4editing')
sys.path.append(encoder4editing_dir)

from StyleCLIP.mapper.scripts.inference import run as run_mapper
from StyleCLIP.mapper.styleclip_mapper import StyleCLIPMapper
from encoder4editing.models.psp import pSp
from PIL import Image

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"]
)


# Create directories
path = '../../../../data/' # path to ur data test :>
RESULTS_DIR = "./results"
os.makedirs(RESULTS_DIR, exist_ok=True)

PRETRAINED_DIR = '../pretrained_models/'
e4e_path = os.path.join(PRETRAINED_DIR, 'e4e_ffhq_encode.pt')


# Setup device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# List of available mappers with their checkpoint paths
AVAILABLE_MAPPERS = {
    "afro": "afro.pt",
    "bobcut": "bobcut.pt",
    "bowlcut": "bowlcut.pt",
    "curly_hair": "curly_hair.pt",
    "mohawk": "mohawk.pt",
    "purple_hair": "purple_hair.pt"
    # "surprised": "surprised.pt"
}

def get_default_args():
    args_dict = {
        'exp_dir': RESULTS_DIR,
        'couple_outputs': True,
        'mapper_type': "LevelsMapper",
        'no_coarse_mapper': False,
        'no_medium_mapper': False,
        'no_fine_mapper': True,
        'stylegan_size': 1024,
        'test_batch_size': 1,
        'test_workers': 1,
        'work_in_stylespace': False,
        'n_images': 1,
        'align': False,
        'device': "cuda"
    }
    return Namespace(**args_dict)

args = get_default_args()

def setup_modele4e(checkpoint_path, device='cuda'):
    ckpt = torch.load(checkpoint_path, map_location='cpu')
    opts = ckpt['opts']

    opts['checkpoint_path'] = checkpoint_path
    opts['device'] = device
    opts = argparse.Namespace(**opts)

    net = pSp(opts)
    net.eval()
    net = net.to(device)
    return net, opts

def setup_e4e(ckpt, device):
    net, opts = setup_modele4e(ckpt, device)
    generator = net.decoder
    generator.eval()
    return net, opts, generator

def setup_mapper(mapper):
    # update test options with options used during training
    ckpt = torch.load(os.path.join(PRETRAINED_DIR, mapper), map_location='cpu')
    opts = ckpt['opts']
    # Update opts with args values
    for key, value in vars(args).items():
        opts[key] = value
    opts['checkpoint_path'] = os.path.join(PRETRAINED_DIR, mapper)
    opts['no_fine_mapper'] = False
    opts = Namespace(**opts)
    # print(opts)
    net = StyleCLIPMapper(opts)
    net.eval()
    net.cuda()
    return net, opts

def setup_step():
    #load checkpoint mapper
    mappers = {}
    for mapper_name, path in AVAILABLE_MAPPERS.items():
        print(f"Load checkpoint of {mapper_name} mapper...")
        net, opts = setup_mapper(path)
        mappers[mapper_name] = {'net': net, 'opts': opts}

    #load e4e
    net_e4e, opts_e4e, generator_e4e = setup_e4e(e4e_path, device)

    return mappers, net_e4e, opts_e4e, generator_e4e

mappers, net_e4e, opts_e4e, generator_e4e = setup_step()


class FunctionName(str, Enum):
    # SURPRISED = "surprised"
    AFRO = "afro"
    BOBCUT = "bobcut"
    BOWLCUT = "bowlcut"
    CURLY_HAIR = "curly_hair"
    MOHAWK = "mohawk"
    PURPLE_HAIR = "purple_hair"

@router.post("/")
async def mapper(
    image: UploadFile = File(...),
    function: FunctionName = Form(...)
):
    try:
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read the uploaded file content
        contents = await image.read()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(image.filename).suffix) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name
        
        try:
            # Validate that image can be opened
            with Image.open(temp_path) as img:
                img.verify()
        except Exception:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Create results directory for this specific run
        unique_id = str(uuid.uuid4())
        results_dir = os.path.join(RESULTS_DIR, unique_id)
        os.makedirs(results_dir, exist_ok=True)
        
        # Create args dictionary
        args.image_path = temp_path
        args.mapper_net = mappers[function]['net']
        args.mapper_opts = mappers[function]['opts']
        args.net_e4e = net_e4e
        args.opts_e4e = opts_e4e
        args.generator_e4e = generator_e4e

        results = run_mapper(args)
        
        if not results:
            raise HTTPException(status_code=500, detail="No results generated")
        
        result = results[0]

        # Convert both original and modified images to base64
        # Original image is already in memory as contents
        original_encoded = base64.b64encode(contents).decode()
        
        with open(result['modified_path'], "rb") as modified_file:
            modified_encoded = base64.b64encode(modified_file.read()).decode()

        # Clean up temporary files
        os.unlink(temp_path)
        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)

        return JSONResponse(content={
            "message": "Mapper run successfully",
            "original_image": original_encoded,
            "modified_image": modified_encoded,
            "format": "base64"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up in case of error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        if 'results_dir' in locals() and os.path.exists(results_dir):
            shutil.rmtree(results_dir)
        
        return JSONResponse(
            content={"message": f"Error: {str(e)}"}, 
            status_code=500
        )


if __name__ == "__main__":
    test_image_path = "/mnt/e/Docs/Nhan_dang/Final_project/data/00000.png" #Change this to your test image path
    print(f"OK1")
    
    if not os.path.exists(test_image_path):
        print(f"image path: {test_image_path}")
        raise FileNotFoundError(f"Test image not found at path: {test_image_path}")
    
    args.image_path = test_image_path
    args.mapper_net = mappers["bobcut"]['net'] 
    args.mapper_opts = mappers["bobcut"]['opts']
    args.net_e4e = net_e4e
    args.opts_e4e = opts_e4e
    args.generator_e4e = generator_e4e

    try:
        print(f"OK2")
        results = run_mapper(args)
        for result in results:
            print(f"Original image path: {result['original_path']}")
            print(f"Modified image path: {result['modified_path']}")
            print(f"Latent path: {result['latent_path']}")
        print("Test completed successfully!")
    except Exception as e:
        print(f"Test failed: {str(e)}")