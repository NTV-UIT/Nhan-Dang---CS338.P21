# Installation Guide

### Yêu cầu hệ thống
- Đã cài đặt Anaconda hoặc Miniconda
- GPU NVIDIA hỗ trợ CUDA (cho phiên bản PyTorch CUDA)
- Python >= 3.9
### Các bước cài đặt

1. Tạo và kích hoạt môi trường conda mới:
```bash
conda create -n styleclip
conda activate styleclip
```
2. Cài đặt PyTorch với hỗ trợ CUDA:
- Check cuda toolkit version:
```bash
nvcc --version
```
- Dựa vào cuda toolkit version (ví dụ: 12.8), ta cài tương ứng bản Pytorch:
```bash
conda install pytorch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia
```

3. Cài đặt TensorFlow:
```bash
pip install tensorflow==2.17.1
```

4. Cài đặt các thư viện bổ sung:
```bash
python -m pip install -r backend/app/requirements.txt
```

5. Check PyTorch CUDA availability:
```python
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'Not available')"
```

6. Check TensorFlow CUDA availability:
```python
python -c "import tensorflow as tf; print('GPU available:', tf.config.list_physical_devices('GPU')); print('TensorFlow version:', tf.__version__)"
```

7. Install ninja:
```python
wget https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip
sudo unzip ninja-linux.zip -d /usr/local/bin/
sudo update-alternatives --install /usr/bin/ninja ninja /usr/local/bin/ninja 1 --force
```
8. Install dlib (Linux only):
```bash
python -m pip install --upgrade pip
python -m pip install cmake dlib
```
- If u get error try [this](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)

9. uvicorn
```bash
python -m pip install --upgrade pip
python -m pip install --force-reinstall --upgrade uvicorn
python -m uvicorn main:app --reload --port 8000
```