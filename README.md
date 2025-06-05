# Installation Guide

## English

### Prerequisites
- Anaconda or Miniconda installed
- NVIDIA GPU with CUDA support (for PyTorch CUDA version)

### Installation Steps

1. Create and activate a new conda environment with Python 3.10:
```bash
conda create -n your_env_name python=3.10
conda activate your_env_name
```

2. Install PyTorch with CUDA 11.8 support:
```bash
python3.10 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. Install TensorFlow:
```bash
python3.10 -m pip install tensorflow==2.17.1
```

4. Install additional requirements:
```bash
python3.10 -m pip install -r requirements.txt
```

## Tiếng Việt

### Yêu cầu hệ thống
- Đã cài đặt Anaconda hoặc Miniconda
- GPU NVIDIA hỗ trợ CUDA (cho phiên bản PyTorch CUDA)

### Các bước cài đặt

1. Tạo và kích hoạt môi trường conda mới với Python 3.10:
```bash
conda create -n your_env_name python=3.10
conda activate your_env_name
```

2. Cài đặt PyTorch với hỗ trợ CUDA 11.8:
```bash
python3.10 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. Cài đặt TensorFlow:
```bash
python3.10 -m pip install tensorflow==2.17.1
```

4. Cài đặt các thư viện bổ sung:
```bash
python3.10 -m pip install -r requirements.txt
``` 