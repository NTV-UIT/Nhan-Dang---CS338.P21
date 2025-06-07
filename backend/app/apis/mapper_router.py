from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import sys
import torchvision
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Add StyleCLIP to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
styleclip_dir = os.path.join(backend_dir, 'StyleCLIP')
sys.path.append(styleclip_dir)

from StyleCLIP.mapper.scripts.inference import run as run_mapper
from PIL import Image

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"]
)

@router.post("/")
async def mapper(
    stylegan_size: int = Form(1024),
    work_in_stylespace: bool = Form(False),
    ckpt: str = Form("./pretrained_models/stylegan2-ffhq-config-f.pt"),
    latent_path: str = Form("./pretrained_models/example_celebs.pt"),
    results_dir: str = Form("../results"),
    ir_se50_weights: str = Form("./pretrained_models/model_ir_se50.pth"),
):
    """Main API endpoint for mapper"""
    try:
        # Create args dictionary instead of using argparse
        args = {
            'exp_dir': results_dir,
            'checkpoint_path': ckpt,
            'couple_outputs': True,
            'mapper_type': "LevelsMapper",
            'no_coarse_mapper': False,
            'no_medium_mapper': False,
            'no_fine_mapper': True,
            'stylegan_size': stylegan_size,
            'latents_test_path': latent_path,
            'test_batch_size': 1,
            'test_workers': 1,
            'work_in_stylespace': work_in_stylespace,
            'n_images': 1,
            'encoder_path': ir_se50_weights
        }
        
        # Convert dict to namespace-like object
        class Args:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        args_obj = Args(**args)
        results = run_mapper(args_obj)
        
        # Get the first result since we only process one image
        result = results[0]
        
        return JSONResponse(content={
            "message": "Mapper run successfully",
            "original_image_path": result['original_path'],
            "modified_image_path": result['modified_path'],
            "latent_path": result['latent_path']
        })
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.exp_dir = "../results/mapper"
    args.checkpoint_path = "../pretrained_models/surprised.pt"
    args.couple_outputs = False
    args.mapper_type = "LevelsMapper"
    args.no_coarse_mapper = False
    args.no_medium_mapper = False
    args.no_fine_mapper = True 
    args.stylegan_size = 1024
    args.latents_test_path = "../pretrained_models/example_celebs.pt"
    args.test_batch_size = 1
    args.test_workers = 1
    args.work_in_stylespace = False
    args.n_images = 1
    
    results = run_mapper(args)
    for result in results:
        if 'original_image' in result:  # Nếu là couple_outputs
            print(f"Original image path: {result['original_path']}")
            print(f"Modified image path: {result['modified_path']}")
        else:
            print(f"Original image path: {result['original_path']}")
            print(f"Image path: {result['image_path']}")
        print(f"Latent path: {result['latent_path']}")