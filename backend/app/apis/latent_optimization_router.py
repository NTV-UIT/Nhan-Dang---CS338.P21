from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import argparse
import os
import sys
import torchvision
from StyleCLIP.optimization.run_optimization import main as run_optimization

# Add StyleCLIP to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
styleclip_dir = os.path.join(backend_dir, 'StyleCLIP')
sys.path.append(styleclip_dir)

router = APIRouter(
    prefix="/latent-optimization",
    tags=["latent-optimization"]
)

@router.post("/")
async def latent_optimization(
    image: UploadFile = File(...),
    text_prompt: str = Form(...),
    id_lambda: float = Form(0.000),
    l2_lambda: float = Form(0.008),
    step: int = Form(300),
    mode: str = Form("edit"),
    lr: float = Form(0.1),
    lr_rampup: float = Form(0.05),
    stylegan_size: int = Form(1024),
    work_in_stylespace: bool = Form(False),
    ckpt: str = Form("./StyleCLIP/pretrained_models/stylegan2-ffhq-config-f.pt"),
    latent_path: str = Form("./StyleCLIP/pretrained_models/example_celebs.pt"),
    results_dir: str = Form("../results"),
    ir_se50_weights: str = Form("./StyleCLIP/pretrained_models/model_ir_se50.pth")
):
    """Main API endpoint for latent optimization"""
    try:
        parser = argparse.ArgumentParser()
        args = parser.parse_args()
        args.description = text_prompt
        args.ckpt = latent_path
        args.stylegan_size = stylegan_size
        args.lr_rampup = lr_rampup
        args.lr = lr
        args.step = step
        args.mode = mode
        args.l2_lambda = l2_lambda
        args.id_lambda = id_lambda
        args.latent_path = latent_path
        args.results_dir = results_dir
        args.ir_se50_weights = ir_se50_weights
        args.work_in_stylespace = work_in_stylespace
        result_image = run_optimization(args)
        
        # Save final result
        final_path = os.path.join(results_dir, "final_result.jpg")
        torchvision.utils.save_image(
            result_image.detach().cpu(), 
            final_path, 
            normalize=True, 
            scale_each=True, 
            value_range=(-1, 1)
        )

        return JSONResponse(
            content={
                "status": "success",
                "message": "Latent optimization completed",
                "result_path": final_path
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

if __name__ == "__main__":
    # Test parameters
    test_params = {
        "text_prompt": "a person with blue hair",
        "id_lambda": 0.000,
        "l2_lambda": 0.008,
        "step": 100,  # Reduced steps for testing
        "mode": "edit",
        "lr": 0.1,
        "lr_rampup": 0.05,
        "stylegan_size": 1024,
        "work_in_stylespace": False,
        "ckpt": "./StyleCLIP/pretrained_models/stylegan2-ffhq-config-f.pt",
        "latent_path": "./StyleCLIP/pretrained_models/example_celebs.pt",
        "ir_se50_weights": "./StyleCLIP/pretrained_models/model_ir_se50.pth",
        "results_dir": "../results"
    }
    
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.description = test_params["text_prompt"]
    args.ckpt = test_params["ckpt"]
    args.stylegan_size = test_params["stylegan_size"]
    args.lr_rampup = test_params["lr_rampup"]
    args.lr = test_params["lr"]
    args.step = test_params["step"]
    args.mode = test_params["mode"]
    args.l2_lambda = test_params["l2_lambda"]
    args.id_lambda = test_params["id_lambda"]
    args.latent_path = test_params["latent_path"]
    args.results_dir = test_params["results_dir"]
    args.ir_se50_weights = test_params["ir_se50_weights"]
    args.work_in_stylespace = test_params["work_in_stylespace"]

    result_image = run_optimization(args)
    
    # Save final result
    final_path = os.path.join(results_dir, "final_result.jpg")
    torchvision.utils.save_image(
        result_image.detach().cpu(), 
        final_path, 
        normalize=True, 
        scale_each=True, 
        value_range=(-1, 1)
    )
    
    print(f"Test completed successfully! Final result saved to {final_path}")