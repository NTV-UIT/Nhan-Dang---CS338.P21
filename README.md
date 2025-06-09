# Hướng dẫn cài đặt & sử dụng dự án StyleCLIP

## 1. Yêu cầu hệ thống
- Đã cài đặt Anaconda hoặc Miniconda
- GPU NVIDIA hỗ trợ CUDA (khuyến nghị)
- Python >= 3.9 ( Tôi sử dụng 3.12.7)
- Node.js >= 16.x (để chạy giao diện web frontend) ( Tôi sử dụng v18.19.1)

## 2. Cài đặt mô hình và phụ thuộc

### 2.1. Tải checkpoints
```bash
cd Nhan-Dang---CS338.P21/backend
mkdir pretrained_models && ./down_ckp.sh
```

### 2.2. Tạo và kích hoạt môi trường conda
```bash
conda create -n styleclip python=3.12.7
conda activate styleclip
```

### 2.3. Cài đặt PyTorch (có CUDA)
- Kiểm tra phiên bản CUDA:
```bash
nvcc --version
```
- Cài đặt PyTorch phù hợp (ví dụ với CUDA 12.4):
```bash
conda install pytorch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia
```

### 2.4. Cài đặt TensorFlow
```bash
python -m pip install tensorflow==2.17.1
```

### 2.5. Cài đặt các thư viện bổ sung
```bash
python -m pip install -r backend/app/requirements.txt
```

### 2.6. Kiểm tra CUDA cho PyTorch & TensorFlow (tuỳ chọn)
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'Not available')"
python -c "import tensorflow as tf; print('GPU available:', tf.config.list_physical_devices('GPU')); print('TensorFlow version:', tf.__version__)"
```

### 2.7. Cài đặt ninja (Linux)
```bash
wget https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip
sudo unzip ninja-linux.zip -d /usr/local/bin/
sudo update-alternatives --install /usr/bin/ninja ninja /usr/local/bin/ninja 1 --force
```

### 2.8. Cài đặt dlib (Linux)
```bash
python -m pip install --upgrade pip
python -m pip install cmake dlib
```
- Nếu gặp lỗi, tham khảo: [Dlib_Windows_Python3.x](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)

## 3. Chạy backend (FastAPI)
```bash
cd backend/app
python -m uvicorn main:app --reload --port 8000
```

## 4. Chạy frontend (React)
```bash
cd my-app
npm install
npm start
```
- Giao diện sẽ chạy tại: http://localhost:3000

## 5. Sử dụng
- Truy cập http://localhost:3000 trên trình duyệt.
- Tải ảnh lên, chọn kiểu tóc và nhấn "Chạy StyleCLIP" để nhận kết quả.

## 6. Ghi chú
- Nếu backend chạy ở port khác, sửa lại URL API trong `my-app/src/App.js` cho phù hợp.
- Đảm bảo backend và frontend cùng chạy để sử dụng đầy đủ chức năng.

---
Nếu gặp lỗi hoặc cần hỗ trợ, hãy kiểm tra lại log terminal hoặc liên hệ người phát triển dự án.
