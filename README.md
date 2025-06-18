# Hướng dẫn cài đặt & sử dụng dự án StyleCLIP

## 1. Cấu trúc thư mục
```
Nhan-Dang---CS338.P21/
├── backend/
│   ├── app/
│   │   ├── StyleCLIP/
│   │   │   ├── mapper/
│   │   │   │   ├── scripts/
│   │   │   │   │   └── results/
│   │   │   │   │       └── evaluation_results/
│   │   │   │   └── models/
│   │   │   └── global_direction/
│   │   ├── encoder4editing/
│   │   ├── stylegan2/
│   │   ├── apis/
│   │   ├── templates/
│   │   ├── static/
│   │   ├── results/
│   │   ├── main.py
│   │   ├── setup.sh
│   │   └── requirements.txt
│   ├── pretrained_models/
│   └── down_ckp.sh
├── my-app/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

### 1.1. Mô tả các thư mục chính
- **backend/app/StyleCLIP/**: Chứa mã nguồn chính của mô hình StyleCLIP
- **backend/app/encoder4editing/**: Mã nguồn cho encoder E4E
- **backend/app/stylegan2/**: Mã nguồn cho mô hình StyleGAN2
- **backend/app/apis/**: Chứa các API endpoints
- **backend/app/templates/**: Chứa các template HTML
- **backend/app/static/**: Chứa các file tĩnh (CSS, JS, images)
- **backend/app/results/**: Thư mục lưu kết quả
- **backend/pretrained_models/**: Chứa các mô hình đã được huấn luyện
- **my-app/**: Mã nguồn frontend React

## 2. Kết quả đánh giá mô hình

### 2.1. So sánh mô hình cũ và mới
- **CLIP Similarity**:
  - Mô hình cũ: 27.7237
  - Mô hình mới: 26.5917
  - Delta CLIP cũ: 0.1540
  - Delta CLIP mới: 0.1720

- **LPIPS (Perceptual Similarity)**:
  - Mô hình cũ vs ảnh gốc: 0.1857
  - Mô hình mới vs ảnh gốc: 0.1728
  - Mô hình cũ vs mô hình mới: 0.0721

- **FID (Fréchet Inception Distance)**:
  - Mô hình cũ vs ảnh gốc: 0.7745
  - Mô hình mới vs ảnh gốc: 0.6210

### 2.2. Phương pháp đánh giá
1. **CLIP Similarity**: Đo lường độ tương đồng ngữ nghĩa giữa ảnh kết quả và prompt text
2. **LPIPS**: Đánh giá sự khác biệt về mặt thị giác giữa các ảnh
3. **FID**: Đo lường chất lượng và tính đa dạng của ảnh được tạo ra
4. **Delta CLIP**: Đánh giá mức độ thay đổi so với ảnh gốc

## 3. Yêu cầu hệ thống
- Đã cài đặt Anaconda hoặc Miniconda
- GPU NVIDIA hỗ trợ CUDA (khuyến nghị)
- Python >= 3.9 ( Tôi sử dụng 3.12.7)
- Node.js >= 16.x (để chạy giao diện web frontend) ( Tôi sử dụng v18.19.1)

## 4. Cài đặt mô hình và phụ thuộc

### 4.1. Tải checkpoints
```bash
cd Nhan-Dang---CS338.P21/backend
mkdir pretrained_models && ./down_ckp.sh
```

### 4.2. Tạo và kích hoạt môi trường conda
```bash
conda create -n styleclip python=3.12.7
conda activate styleclip
```

### 4.3. Cài đặt PyTorch (có CUDA)
- Kiểm tra phiên bản CUDA:
```bash
nvcc --version
```
- Cài đặt PyTorch phù hợp (ví dụ với CUDA 12.4):
```bash
conda install pytorch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia
```

### 4.4. Cài đặt TensorFlow
```bash
python -m pip install tensorflow==2.17.1
```

### 4.5. Cài đặt các thư viện bổ sung
```bash
python -m pip install -r backend/app/requirements.txt
```

### 4.6. Kiểm tra CUDA cho PyTorch & TensorFlow (tuỳ chọn)
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'Not available')"
python -c "import tensorflow as tf; print('GPU available:', tf.config.list_physical_devices('GPU')); print('TensorFlow version:', tf.__version__)"
```

### 4.7. Cài đặt ninja (Linux)
```bash
wget https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip
sudo unzip ninja-linux.zip -d /usr/local/bin/
sudo update-alternatives --install /usr/bin/ninja ninja /usr/local/bin/ninja 1 --force
```

### 4.8. Cài đặt dlib (Linux)
```bash
python -m pip install --upgrade pip
python -m pip install cmake dlib
```
- Nếu gặp lỗi, tham khảo: [Dlib_Windows_Python3.x](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)

## 5. Chạy backend (FastAPI)
```bash
cd backend/app
python -m uvicorn main:app --reload --port 8000
```

## 6. Chạy frontend (React)
```bash
cd my-app
npm install
npm start
```
- Giao diện sẽ chạy tại: http://localhost:3000

## 7. Sử dụng
- Truy cập http://localhost:3000 trên trình duyệt.
- Tải ảnh lên, chọn kiểu tóc và nhấn "Chạy StyleCLIP" để nhận kết quả.

## 8. Ghi chú
- Nếu backend chạy ở port khác, sửa lại URL API trong `my-app/src/App.js` cho phù hợp.
- Đảm bảo backend và frontend cùng chạy để sử dụng đầy đủ chức năng.

---
Nếu gặp lỗi hoặc cần hỗ trợ, hãy kiểm tra lại log terminal hoặc liên hệ người phát triển dự án.
