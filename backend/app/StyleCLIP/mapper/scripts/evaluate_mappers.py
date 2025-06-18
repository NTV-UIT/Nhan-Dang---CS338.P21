import os
import sys
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
from PIL import Image
import lpips
from torchmetrics.image.fid import FrechetInceptionDistance
import clip
import argparse
from argparse import Namespace
from inference import run_on_batch

# Add StyleCLIP root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
mapper_dir = os.path.dirname(current_dir)  # mapper directory
styleclip_dir = os.path.dirname(os.path.dirname(current_dir))  # StyleCLIP root
sys.path.extend([mapper_dir, styleclip_dir])

# Import mapper modules
from mapper.latent_mappers_original import SingleMapper as SingleMapperOld, LevelsMapper as LevelsMapperOld, WithoutToRGBStyleSpaceMapper as WithoutToRGBStyleSpaceMapperOld
from mapper.latent_mappers import SingleMapper, LevelsMapper, WithoutToRGBStyleSpaceMapper
from mapper.training.train_utils import convert_s_tensor_to_list
from mapper.datasets.latents_dataset import LatentsDataset, StyleSpaceLatentsDataset
from mapper.options.test_options import TestOptions
from inference import setup_e4e, setup_mapper, inversion
from models.stylegan2.model import Generator
from mapper.styleclip_mapper import StyleCLIPMapper, SingleMapper, LevelsMapper, WithoutToRGBStyleSpaceMapper
from mapper.styleclip_mapper_old import StyleCLIPMapper as StyleCLIPMapperOld, SingleMapper as SingleMapperOld, LevelsMapper as LevelsMapperOld, WithoutToRGBStyleSpaceMapper as WithoutToRGBStyleSpaceMapperOld


class MapperEvaluator:
    def __init__(self, device='cuda', seed=42):
        self.device = device
        self.seed = seed
        # Set random seeds for reproducibility
        torch.manual_seed(seed)
        np.random.seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        self.setup_metrics()
        
    def setup_metrics(self):
        # Setup LPIPS
        self.lpips_fn = lpips.LPIPS(net='alex').to(self.device)
        
        # Setup FID
        self.fid = FrechetInceptionDistance(feature=64).to(self.device)
        
        # Setup CLIP
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
        
    def compute_clip_similarity(self, image, text_prompt):
        # Convert tensor to PIL Image
        if isinstance(image, torch.Tensor):
            # Denormalize if needed (assuming image is in [-1, 1] range)
            if image.min() < 0:
                image = (image + 1) / 2
            # Convert to [0, 255] range
            image = (image * 255).clamp(0, 255).to(torch.uint8)
            # Convert to PIL Image
            image = transforms.ToPILImage()(image.squeeze(0))
        
        # Preprocess image for CLIP
        image = transforms.Resize((224, 224))(image)
        image = self.clip_preprocess(image).unsqueeze(0).to(self.device)
        
        # Encode text prompt
        text = clip.tokenize([text_prompt]).to(self.device)
        
        # Get embeddings
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image)
            text_features = self.clip_model.encode_text(text)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Compute similarity
            similarity = (100.0 * image_features @ text_features.T).item()
            
        return similarity
    
    def compute_lpips(self, img1, img2):
        # Ensure both images are in the same range and format
        if isinstance(img1, torch.Tensor):
            if img1.min() < 0:
                img1 = (img1 + 1) / 2
            img1 = img1.clamp(0, 1)
        if isinstance(img2, torch.Tensor):
            if img2.min() < 0:
                img2 = (img2 + 1) / 2
            img2 = img2.clamp(0, 1)
        
        # Resize both images to the same size (256x256)
        img1 = transforms.Resize((256, 256))(img1)
        img2 = transforms.Resize((256, 256))(img2)
        
        # Ensure both images are on the same device
        img1 = img1.to(self.device)
        img2 = img2.to(self.device)
        
        # Compute LPIPS
        return self.lpips_fn(img1, img2).item()
    
    def compute_fid(self, real_images, fake_images):
        self.fid.update(real_images, real=True)
        self.fid.update(fake_images, real=False)
        return self.fid.compute().item()
    
    def setup_mapper(self, mapper_path, is_old_mapper=False):
        """Setup mapper with correct class based on whether it's old or new"""
        # Load checkpoint and update options
        ckpt = torch.load(mapper_path, map_location='cpu')
        opts = ckpt['opts']
        opts = Namespace(**opts)
        opts.checkpoint_path = mapper_path  # Set checkpoint path for loading weights
        
        # Create StyleCLIPMapper with appropriate class
        if is_old_mapper:
            mapper = StyleCLIPMapperOld(opts)
        else:
            mapper = StyleCLIPMapper(opts)
            
        mapper.eval()
        mapper = mapper.to(self.device)
        return mapper, opts
    
    def evaluate_mappers(self, test_opts, old_mapper_path, new_mapper_path, prompt, n_images=10):
        # Setup old and new mappers
        old_mapper, old_opts = self.setup_mapper(old_mapper_path, is_old_mapper=True)
        new_mapper, new_opts = self.setup_mapper(new_mapper_path, is_old_mapper=False)
        
        # Initialize metrics
        metrics = {
            'clip_similarity_old': [],
            'clip_similarity_new': [],
            'lpips_old_vs_original': [],
            'lpips_new_vs_original': [],
            'lpips_old_vs_new': [],
            'fid_old_vs_original': None,
            'fid_new_vs_original': None
        }
        
        # Create output directory
        out_path = os.path.join(test_opts.exp_dir, 'evaluation_results')
        os.makedirs(out_path, exist_ok=True)
        
        # Load pre-existing latents
        print("Loading pre-existing latents...")
        test_latents = torch.load(test_opts.latents_test_path)
        if n_images < len(test_latents):
            test_latents = test_latents[:n_images]
            
        # Create dataset and dataloader
        if old_opts.work_in_stylespace:
            dataset = StyleSpaceLatentsDataset(latents=[l.cpu() for l in test_latents], opts=old_opts)
        else:
            dataset = LatentsDataset(latents=test_latents.cpu(), opts=old_opts)
            
        dataloader = DataLoader(dataset,
                              batch_size=old_opts.test_batch_size,
                              shuffle=False,
                              num_workers=int(old_opts.test_workers),
                              drop_last=True)
        
        # Chuẩn bị embedding cho ΔCLIP
        text_edit_emb = self.get_clip_text_embedding(prompt)
        text_neutral_emb = self.get_clip_text_embedding('a face')
        text_direction = text_edit_emb - text_neutral_emb
        delta_clip_old_list = []
        delta_clip_new_list = []
        
        # Reset FID
        self.fid.reset()
        
        # Process images
        num_saved = 0
        for input_batch in tqdm(dataloader):
            with torch.no_grad():
                if old_opts.work_in_stylespace:
                    input_cuda = convert_s_tensor_to_list(input_batch)
                    input_cuda = [c.to(self.device) for c in input_cuda]
                else:
                    input_cuda = input_batch.to(self.device)
                
                # Sinh ảnh bằng run_on_batch giống inference.py
                old_image, _, original_image = run_on_batch(input_cuda, old_mapper, couple_outputs=True, stylespace=old_opts.work_in_stylespace)
                new_image, _, _ = run_on_batch(input_cuda, new_mapper, couple_outputs=False, stylespace=new_opts.work_in_stylespace)
                
                # Chuyển ảnh về dạng uint8 [0,255] cho FID và đảm bảo cùng device
                orig_fid = self.preprocess_for_fid(original_image).to(self.device)
                old_fid = self.preprocess_for_fid(old_image).to(self.device)
                new_fid = self.preprocess_for_fid(new_image).to(self.device)
                
                # Update FID từng batch
                self.fid.update(orig_fid, real=True)
                self.fid.update(old_fid, real=False)
                
                # Process each image in the batch
                for i in range(old_opts.test_batch_size):
                    # Compute metrics
                    metrics['clip_similarity_old'].append(self.compute_clip_similarity(old_image[i], prompt))
                    metrics['clip_similarity_new'].append(self.compute_clip_similarity(new_image[i], prompt))
                    metrics['lpips_old_vs_original'].append(self.compute_lpips(old_image[i], original_image[i]))
                    metrics['lpips_new_vs_original'].append(self.compute_lpips(new_image[i], original_image[i]))
                    metrics['lpips_old_vs_new'].append(self.compute_lpips(old_image[i], new_image[i]))

                    # ΔCLIP cho old mapper
                    old_img_emb = self.get_clip_image_embedding(old_image[i])
                    orig_img_emb = self.get_clip_image_embedding(original_image[i])
                    img_direction_old = old_img_emb - orig_img_emb
                    delta_clip_old = torch.nn.functional.cosine_similarity(img_direction_old.unsqueeze(0), text_direction.unsqueeze(0)).item()
                    delta_clip_old_list.append(delta_clip_old)

                    # ΔCLIP cho new mapper
                    new_img_emb = self.get_clip_image_embedding(new_image[i])
                    img_direction_new = new_img_emb - orig_img_emb
                    delta_clip_new = torch.nn.functional.cosine_similarity(img_direction_new.unsqueeze(0), text_direction.unsqueeze(0)).item()
                    delta_clip_new_list.append(delta_clip_new)
                    
                    # Save images for visualization (chỉ lưu 10 ảnh đầu)
                    if num_saved < 10:
                        torchvision.utils.save_image(original_image[i], os.path.join(out_path, f'original_{num_saved:05d}.jpg'), normalize=True, value_range=(-1, 1))
                        torchvision.utils.save_image(old_image[i], os.path.join(out_path, f'old_mapper_{num_saved:05d}.jpg'), normalize=True, value_range=(-1, 1))
                        torchvision.utils.save_image(new_image[i], os.path.join(out_path, f'new_mapper_{num_saved:05d}.jpg'), normalize=True, value_range=(-1, 1))
                        num_saved += 1
                
                # Giải phóng bộ nhớ
                del original_image, old_image, new_image, orig_fid, old_fid, new_fid
                torch.cuda.empty_cache()
        
        # Tính FID sau khi xử lý hết các batch
        metrics['fid_old_vs_original'] = self.fid.compute().item()
        
        # Reset FID và tính cho new mapper
        self.fid.reset()
        for input_batch in dataloader:
            with torch.no_grad():
                if old_opts.work_in_stylespace:
                    input_cuda = convert_s_tensor_to_list(input_batch)
                    input_cuda = [c.to(self.device) for c in input_cuda]
                else:
                    input_cuda = input_batch.to(self.device)
                
                # Sinh ảnh
                original_image, _, _ = run_on_batch(input_cuda, old_mapper, couple_outputs=True, stylespace=old_opts.work_in_stylespace)
                new_image, _, _ = run_on_batch(input_cuda, new_mapper, couple_outputs=False, stylespace=new_opts.work_in_stylespace)
                
                # Chuyển ảnh về dạng uint8 [0,255] cho FID
                orig_fid = self.preprocess_for_fid(original_image).to(self.device)
                new_fid = self.preprocess_for_fid(new_image).to(self.device)
                
                # Update FID
                self.fid.update(orig_fid, real=True)
                self.fid.update(new_fid, real=False)
                
                # Giải phóng bộ nhớ
                del original_image, new_image, orig_fid, new_fid
                torch.cuda.empty_cache()
        
        metrics['fid_new_vs_original'] = self.fid.compute().item()
        
        # Compute average metrics
        results = {
            'avg_clip_similarity_old': np.mean(metrics['clip_similarity_old']),
            'avg_clip_similarity_new': np.mean(metrics['clip_similarity_new']),
            'delta_clip_old': np.mean(delta_clip_old_list),  # ΔCLIP old
            'delta_clip_new': np.mean(delta_clip_new_list),  # ΔCLIP new
            'avg_lpips_old_vs_original': np.mean(metrics['lpips_old_vs_original']),
            'avg_lpips_new_vs_original': np.mean(metrics['lpips_new_vs_original']),
            'avg_lpips_old_vs_new': np.mean(metrics['lpips_old_vs_new']),
            'fid_old_vs_original': metrics['fid_old_vs_original'],
            'fid_new_vs_original': metrics['fid_new_vs_original']
        }
        
        # Save results
        with open(os.path.join(out_path, 'evaluation_results.txt'), 'w') as f:
            f.write(f"Evaluation with seed: {self.seed}\n")
            f.write(f"Number of images: {len(metrics['clip_similarity_old'])}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"Old mapper: {old_mapper_path}\n")
            f.write(f"New mapper: {new_mapper_path}\n\n")
            for metric, value in results.items():
                if value is not None:
                    f.write(f'{metric}: {value:.4f}\n')
                else:
                    f.write(f'{metric}: None\n')
        
        return results

    def preprocess_for_fid(self, imgs):
        # imgs: (N, C, H, W), float [-1,1] hoặc [0,1] -> uint8 [0,255]
        if imgs.min() < 0:
            imgs = (imgs + 1) / 2  # [-1,1] -> [0,1]
        imgs = (imgs * 255).clamp(0, 255).to(torch.uint8)
        return imgs

    def get_clip_image_embedding(self, image):
        # Đưa ảnh về đúng range và kích thước cho CLIP
        if isinstance(image, torch.Tensor):
            if image.min() < 0:
                image = (image + 1) / 2
            image = (image * 255).clamp(0, 255).to(torch.uint8)
            image = transforms.ToPILImage()(image.squeeze(0))
        image = transforms.Resize((224, 224))(image)
        image = self.clip_preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.squeeze(0)

    def get_clip_text_embedding(self, text):
        text = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            text_features = self.clip_model.encode_text(text)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.squeeze(0)

def main():
    # Setup test options
    test_opts = TestOptions().parse()
    test_opts.exp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    test_opts.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    test_opts.latents_test_path = '../../../../pretrained_models/test_faces.pt'
    
    # Initialize evaluator with fixed seed
    evaluator = MapperEvaluator(device=test_opts.device, seed=42)
    
    # Run evaluation
    results = evaluator.evaluate_mappers(
        test_opts=test_opts,
        old_mapper_path='../../../../pretrained_models/bobcut_old.pt',
        new_mapper_path='../../../../pretrained_models/bobcut.pt',
        prompt='bobcut',
        n_images=1000
    )
    
    print("Evaluation Results:")
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}")

if __name__ == '__main__':
    main() 