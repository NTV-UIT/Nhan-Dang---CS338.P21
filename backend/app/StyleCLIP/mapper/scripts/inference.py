import os
from argparse import Namespace

import torchvision
import numpy as np
import torch
from torch.utils.data import DataLoader
import sys
import time
from PIL import Image
from tqdm import tqdm
from torchvision import transforms
import dlib

# Add StyleCLIP root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
styleclip_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(styleclip_dir)

# Add encoder4editing to Python path
encoder4editing_dir = os.path.join(os.path.dirname(styleclip_dir), 'encoder4editing')
sys.path.append(encoder4editing_dir)

from ..training.train_utils import convert_s_tensor_to_list
from ..datasets.latents_dataset import LatentsDataset, StyleSpaceLatentsDataset
from ..options.test_options import TestOptions
from ..styleclip_mapper import StyleCLIPMapper
import argparse

from encoder4editing.models.psp import pSp

def setup_model(checkpoint_path, device='cuda'):
    ckpt = torch.load(checkpoint_path, map_location='cpu')
    opts = ckpt['opts']

    opts['checkpoint_path'] = checkpoint_path
    opts['device'] = device
    opts = argparse.Namespace(**opts)

    net = pSp(opts)
    net.eval()
    net = net.to(device)
    return net, opts

def get_latents(net, x, is_cars=False):
    codes = net.encoder(x)
    if net.opts.start_from_latent_avg:
        if codes.ndim == 2:
            codes = codes + net.latent_avg.repeat(codes.shape[0], 1, 1)[:, 0, :]
        else:
            codes = codes + net.latent_avg.repeat(codes.shape[0], 1, 1)
    if codes.shape[1] == 18 and is_cars:
        codes = codes[:, :16, :]
    return codes

def get_all_latents(net, x, is_cars=False, device='cuda'):
    with torch.no_grad():
        inputs = x.to(device).float()
        latents = get_latents(net, inputs, is_cars)
    return latents

def run_alignment(image_path):
    predictor = dlib.shape_predictor(paths_config.model_paths['shape_predictor'])
    aligned_image = align_face(filepath=image_path, predictor=predictor)
    print("Aligned image has shape: {}".format(aligned_image.size))
    return aligned_image

def setup_data_loader(align, image_path, opts):
    # Define transforms directly
    transform_test = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    
    # Run alignment if needed
    if align:
        image = run_alignment(image_path)
    else:
        image = Image.open(image_path)
        
    # Apply transform
    image = transform_test(image)
    image = image.unsqueeze(0)  # Add batch dimension
    
    return image

@torch.no_grad()
def generate_inversions(test_opts, g, latent_codes, is_cars):
    print('Saving inversion images')
    inversions_directory_path = os.path.join(test_opts.save_dir, 'inversions')
    os.makedirs(inversions_directory_path, exist_ok=True)
    imgs, _ = g([latent_codes[i].unsqueeze(0)], input_is_latent=True, randomize_noise=False, return_latents=True)
    if is_cars:
        imgs = imgs[:, :, 64:448, :]
    save_image(imgs[0], inversions_directory_path, i + 1)

def setup_e4e(ckpt, device):
    net, opts = setup_model(ckpt, device)
    generator = net.decoder
    generator.eval()
    return net, opts, generator

def inversion(test_opts, device='cuda', align=False, image_path=None):
    # net, opts, generator = setup_e4e(ckpt, device)
    net, opts, generator = test_opts.net_e4e, test_opts.opts_e4e, test_opts.generator_e4e
    is_cars = 'cars_' in opts.dataset_type
    image = setup_data_loader(align, image_path, opts)
    latent_codes = get_all_latents(net, image, is_cars=is_cars, device=device)
    # generate_inversions(test_opts, generator, latent_codes, is_cars)
    return latent_codes

def setup_mapper(test_opts):
    # update test options with options used during training
    ckpt = torch.load(test_opts.checkpoint_path, map_location='cpu')
    opts = ckpt['opts']
    opts.update(vars(test_opts))
    opts = Namespace(**opts)

    net = StyleCLIPMapper(opts)
    net.eval()
    net.cuda()
    return net, opts

def run(test_opts):
    out_path_results = os.path.join(test_opts.exp_dir, 'inference_results')
    os.makedirs(out_path_results, exist_ok=True)

    # net, opts = setup_mapper(test_opts)
    net, opts = test_opts.mapper_net, test_opts.mapper_opts

    # test_latents = torch.load(opts.latents_test_path)
    test_latents = inversion(test_opts, device=test_opts.device, align=test_opts.align, image_path=test_opts.image_path)
    
    print(f"test_latents: {test_latents.shape}")
    if opts.work_in_stylespace:
        dataset = StyleSpaceLatentsDataset(latents=[l.cpu() for l in test_latents], opts=opts)
    else:
        dataset = LatentsDataset(latents=test_latents.cpu(), opts=opts)
    dataloader = DataLoader(dataset,
                            batch_size=opts.test_batch_size,
                            shuffle=False,
                            num_workers=int(opts.test_workers),
                            drop_last=True)

    if opts.n_images is None:
        opts.n_images = len(dataset)
    
    global_i = 0
    global_time = []
    results = []  # List to store results for each image
    for input_batch in tqdm(dataloader):
        if global_i >= opts.n_images:
            break
        with torch.no_grad():
            if opts.work_in_stylespace:
                input_cuda = convert_s_tensor_to_list(input_batch)
                input_cuda = [c.cuda() for c in input_cuda]
            else:
                input_cuda = input_batch
                input_cuda = input_cuda.cuda()

            tic = time.time()
            result_batch = run_on_batch(input_cuda, net, opts.couple_outputs, opts.work_in_stylespace)
            toc = time.time()
            global_time.append(toc - tic)

        for i in range(opts.test_batch_size):
            im_path = str(global_i).zfill(5)
            if test_opts.couple_outputs:
                # Save original image
                original_path = os.path.join(out_path_results, f"original_{im_path}.jpg")
                torchvision.utils.save_image(result_batch[2][i], original_path, normalize=True, value_range=(-1, 1))
                
                # Save modified image
                modified_path = os.path.join(out_path_results, f"modified_{im_path}.jpg")
                torchvision.utils.save_image(result_batch[0][i], modified_path, normalize=True, value_range=(-1, 1))
                
                # Save latent
                latent_path = os.path.join(out_path_results, f"latent_{im_path}.pt")
                torch.save(result_batch[1][i].detach().cpu(), latent_path)
                
                # Store results
                results.append({
                    'original_image': result_batch[2][i],
                    'modified_image': result_batch[0][i],
                    'original_path': original_path,
                    'modified_path': modified_path,
                    'latent_path': latent_path
                })
            else:
                # Save original image
                original_path = os.path.join(out_path_results, f"original_{im_path}.jpg")
                torchvision.utils.save_image(result_batch[2][i], original_path, normalize=True, value_range=(-1, 1))
                
                # Save modified image
                modified_path = os.path.join(out_path_results, f"modified_{im_path}.jpg")
                torchvision.utils.save_image(result_batch[0][i], modified_path, normalize=True, value_range=(-1, 1))
                
                # Save latent
                latent_path = os.path.join(out_path_results, f"latent_{im_path}.pt")
                torch.save(result_batch[1][i].detach().cpu(), latent_path)
                
                # Store results
                results.append({
                    'original_image': result_batch[2][i],
                    'modified_image': result_batch[0][i],
                    'original_path': original_path,
                    'modified_path': modified_path,
                    'latent_path': latent_path
                })

            global_i += 1

    stats_path = os.path.join(opts.exp_dir, 'stats.txt')
    if global_time:  # Only calculate stats if we have results
        result_str = 'Runtime {:.4f}+-{:.4f}'.format(np.mean(global_time), np.std(global_time))
    else:
        result_str = 'No results to calculate runtime statistics'
    print(result_str)

    with open(stats_path, 'w') as f:
        f.write(result_str)
        
    return results  # Return the list of results

def run_on_batch(inputs, net, couple_outputs=False, stylespace=False):
    w = inputs
    with torch.no_grad():
        if stylespace:
            delta = net.mapper(w)
            w_hat = [c + 0.1 * delta_c for (c, delta_c) in zip(w, delta)]
            x_hat, _, w_hat = net.decoder([w_hat], input_is_latent=True, return_latents=True,
                                           randomize_noise=False, truncation=1, input_is_stylespace=True)
        else:
            w_hat = w + 0.1 * net.mapper(w)
            x_hat, w_hat, _ = net.decoder([w_hat], input_is_latent=True, return_latents=True,
                                           randomize_noise=False, truncation=1)
        
        if couple_outputs:
            x, _ = net.decoder([w], input_is_latent=True, randomize_noise=False, truncation=1, input_is_stylespace=stylespace)
            return x_hat, w_hat, x
        else:
            # Generate original image for non-couple case
            x, _ = net.decoder([w], input_is_latent=True, randomize_noise=False, truncation=1, input_is_stylespace=stylespace)
            return x_hat, w_hat, x

if __name__ == '__main__':
    test_opts = TestOptions().parse()
    run(test_opts)
