import torch
from torch.utils.data import Dataset
from PIL import Image
import os
import json
import torchvision.transforms as transforms

class CelebAHQDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.image_dir = os.path.join(root_dir, 'images')
        self.attr_file = os.path.join(root_dir, 'attributes.json')
        
        # Load image paths and attributes
        with open(self.attr_file, 'r') as f:
            self.attributes = json.load(f)
        
        self.image_paths = list(self.attributes.keys())
        
        # Default transform
        if transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ])
        else:
            self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.image_paths[idx])
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        # Get attributes for text prompt generation
        attrs = self.attributes[self.image_paths[idx]]
        text_prompt = self.generate_text_prompt(attrs)
        
        return image, text_prompt
    
    def generate_text_prompt(self, attrs):
        # Convert attributes to text prompt
        prompt_parts = []
        for attr, value in attrs.items():
            if value:
                prompt_parts.append(attr)
        
        return " ".join(prompt_parts)

class RAFDDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.image_dir = os.path.join(root_dir, 'raf-basic')
        
        # Get all image paths
        self.image_paths = []
        for root, _, files in os.walk(self.image_dir):
            for file in files:
                if file.endswith(('.jpg', '.png', '.jpeg')):
                    self.image_paths.append(os.path.join(root, file))
        
        # Default transform
        if transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ])
        else:
            self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        # Get emotion from directory name
        emotion = os.path.basename(os.path.dirname(img_path))
        text_prompt = f"a person with {emotion} expression"
        
        return image, text_prompt

class FaceDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.image_dir = os.path.join(root_dir, 'images')
        
        # Lấy danh sách tất cả các file ảnh
        self.image_paths = [f for f in os.listdir(self.image_dir) 
                          if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        # Default transform
        if transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ])
        else:
            self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.image_paths[idx])
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        # Trả về ảnh và text prompt đơn giản
        return image, "a face"

label2emotion = {
    0: "neutral",
    1: "happy",
    2: "sad",
    3: "surprised",
    4: "angry",
    5: "disgusted",
    6: "fearful"
}

class CustomRAFDDataset(Dataset):
    def __init__(self, root_dir, label_file, transform=None):
        self.root_dir = root_dir
        self.label_file = label_file
        self.samples = []
        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    img_name, label = parts
                    self.samples.append((img_name, int(label)))
        if transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ])
        else:
            self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_name, label = self.samples[idx]
        img_path = os.path.join(self.root_dir, "Image", img_name)
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        emotion = label2emotion[label]
        text_prompt = f"a person with {emotion} expression"
        return image, text_prompt 