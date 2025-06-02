from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import argparse
import os
import sys
import torchvision
# Add StyleCLIP to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
styleclip_dir = os.path.join(backend_dir, 'StyleCLIP')
sys.path.append(styleclip_dir)

from mapper.scripts.inference import run as run_mapper
from PIL import Image

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"]
)

@app.post("/")
async def mapper(
    stylegan_size: int = Form(1024),
    work_in_stylespace: bool = Form(False),
    ckpt: str = Form("./StyleCLIP/pretrained_models/stylegan2-ffhq-config-f.pt"),
    latent_path: str = Form("./StyleCLIP/pretrained_models/example_celebs.pt"),
    results_dir: str = Form("../results"),
    ir_se50_weights: str = Form("./StyleCLIP/pretrained_models/model_ir_se50.pth")
):
    """Main API endpoint for mapper"""
    try:
        parser = argparse.ArgumentParser()
        args = parser.parse_args()
        args.exp_dir = results_dir
        args.checkpoint_path = ckpt
        args.couple_outputs = True
        args.mapper_type = "LevelsMapper"
        args.no_coarse_mapper = False
        args.no_medium_mapper = False
        args.no_fine_mapper = True 
        args.stylegan_size = stylegan_size
        args.latents_test_path = latent_path
        args.test_batch_size = 2
        args.test_workers = 2
        args.work_in_stylespace = work_in_stylespace
        args.n_images = None
        
        run_mapper(args)
        
        return JSONResponse(content={"message": "Mapper run successfully"})
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)
        
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.exp_dir = "../results/mapper"
    args.checkpoint_path = "./StyleCLIP/pretrained_models/surprised.pt"
    args.couple_outputs = True
    args.mapper_type = "LevelsMapper"
    args.no_coarse_mapper = False
    args.no_medium_mapper = False
    args.no_fine_mapper = True 
    args.stylegan_size = 1024
    args.latents_test_path = "./StyleCLIP/pretrained_models/example_celebs.pt"
    args.test_batch_size = 2
    args.test_workers = 2
    args.work_in_stylespace = False
    args.n_images = None
    
    run_mapper(args)
